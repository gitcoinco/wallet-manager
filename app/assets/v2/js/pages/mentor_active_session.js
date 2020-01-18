// TODO: capitasation

// Test DAI have 18 decimals
const TESTDAI_DECIMAL = Math.pow(10, 18);
// Waiting time between approval and attempting to call the contract (in ms)
const CONFIRMATION_WAIT_TIME = 30000;
// Delay before stream startTime (in ms)
const STREAM_START_TIME_DELAY = 300000;

// Find the closer multiple
const closerMultiple = (deposit, delta) => deposit - (deposit % delta);
// Show an element if a condition is filled, hide it otherwise
const showIf = (condition, element) =>
  conndition ? element.show() : element.hide();

const startEarningRefresh = function(stream) {
  const { startTime, endTime } = stream;
  const refresh = setInterval(() => {
    const now = Math.round(new Date().getTime() / 1000);
    const diff = startTime - now;

    $(".diff .min").text(Math.floor(diff / 60));
    $(".diff .sec").text(diff % 60);

    const total = endTime - startTime;
    $(".total .min").text(Math.floor(total / 60));
    $(".total .sec").text(total % 60);

    const depositDai = stream.deposit / TESTDAI_DECIMAL;
    $(".deposit-dai").text(depositDai.toFixed(2));

    const streamedDai = ((diff / total) * deposit) / TESTDAI_DECIMAL;
    $(".streamed-dai").text(streamedDai.toFixed(2));

		// TODO: handle end of stream
  });
};

const startStreamCountdown = function(stream) {
  const { startTime, endTime } = stream;
  const countDown = setInterval(() => {
    const now = Math.round(new Date().getTime() / 1000);
    const diff = startTime - now;
    const diffMin = Math.floor(diff / 60);
    const diffSec = y % 60;
    $(".wait-stream .min").text(diffMin);
    showIf(diffMin < 0, $(".wait-stream .if-min"));
    $(".wait-stream .sec").text(diffSec);

    if (now > startTime) {
      $(".main").show();
      $(".wait-stream").hide();
      clearInterval(countDown);
      startEarningRefresh({ startTime, endTime });
    }
  }, 1000);
};

$(document).ready(function() {
  // Connect the videoplayer

  /*
			const domain = 'meet.jit.si';
			const options = {
					roomName: room_address,
					width: 700,
					height: 700,
					parentNode: document.querySelector('#jitsy-placeholder')
			};
			const api = new JitsiMeetExternalAPI(domain, options);
			*/

  $(".main").hide();
  $(".wait-stream").hide();
  $(".wait-stream-register").hide();

  ethereum.enable().then(([address]) => {
    // Pool to recover stream from Sablier API

    console.log("address", address);
    const query = `
			{
				streams (where: {recipient: "${room_address}"}) {
					id
					deposit
					sender
					recipient
					startTime
					stopTime
				}
			}
		`;

    console.log("query", query);

    const pooling = setInterval(() => {
      fetch(
        "https://api.thegraph.com/subgraphs/name/sablierhq/sablier-rinkeby",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query })
        }
      )
        .then(answer => answer.json())
        .then(answer => {
          console.log("answer", answer);
          // Find if there's a next stream
          if (answer.data.streams.length) {
            const now = Math.round(new Date().getTime() / 1000);
            const streams = answer.data.streams.sort(
              (a, b) => a.startTime < b.startTime
            );
            console.log("streams", streams);

            const ongoingStream = streams.find(
              stream => stream.startTime < now && now < stream.endTime
            );
            console.log("ongoingStream", ongoingStream);

            if (ongoingStream) {
              // TODO: Check if the user is the sender or the reciever
              // of the stream
              startEarningRefresh(ongoingStream);
              clearInterval(pooling);
              $(".main").show();
              $(".wait").hide();
            }

            const nextStream = streams.find(stream => stream.startTime > now);
            console.log("nextStream", nextStream);

            if (nextStream) {
              startStreamCountdown(nextStream);
              clearInterval(pooling);

              $(".main").show();
              $(".wait").hide();
            }
          }
        });
    }, 10000);

    // Check if the user is the room owner
    if (room_address === address) {
      $(".wait").show();
    } else {
      $(".create-stream").show();
    }

    // Load contracts

    const sablier_contract = web3.eth
      .contract(sablier_abi)
      .at(sablier_address());
    const testdai_contract = web3.eth.contract(token_abi).at(testdai_address());

    // Create the stream

    $(".create-btn").click(() => {
      const depositMin = parseInt($("#deposit").val());
      if (depositMin === NaN) return;
      // TODO: show an error message

      const mentor_address = room_address;

      // Compute a deposit_rounded (deposit should be a multiple of delta)
      const now = Math.round(new Date().getTime() / 1000);
      const startTime = now + STREAM_START_TIME_DELAY;
      const stopTime = now + STREAM_START_TIME_DELAY + depositMin;
      const delta = stopTime - startTime;
      const deposit = depositMin * rate_per_min;
      const deposit_rounded = closerMultiple(deposit, delta);

      if (deposit_rounded % delta) throw "Not multiple";
      if (now > startTime) throw "startTime should be in the future";
      if (startTime > stopTime) throw "endTime should be after startTime";

      console.warn("mentor_address", mentor_address);

      console.warn("deposit", deposit);
      console.warn("deposit_rounded", deposit_rounded);
      console.warn("deposit in dai", deposit / 1000000000000000000);
      console.warn("now", now);
      console.warn("startTime", startTime);
      console.warn("stopTime", stopTime);

      testdai_contract.approve(sablier_address(), deposit, () => {
        setTimeout(() => {
          $(".wait-stream-register").show();
          $(".create-stream").hide();
          console.warn(
            "creating the stream at ",
            Math.round(new Date().getTime() / 1000)
          );
          sablier_contract.createStream(
            mentor_address,
            deposit_rounded,
            testdai_address(),
            startTime,
            stopTime,
            () => {
              // Wait for the beginning of the stream
              console.warn("DONE", Math.round(new Date().getTime() / 1000));
            }
          );
        }, CONFIRMATION_WAIT_TIME);
      });
    });

    // Stop the stream
    // TODO: react to button click

    $("stop-stream-btn").click(() => {
      sablier_contract.cancelStream(currentStream.id, () => {
        // TODO: come back to default state
      });
    });

    // Withdraw money
    $("withdraw-btn").click(() => {
      // TODO: show a dialog to ask how much to withdraw
      const sum = parseInt($("withdraw-btn-show").val());
      sablier_contract.takeEarnings(address, sum, () => {
        // 	TODO: show a dialog to signal the user fund
        //	have been withdrawn
      });
    });
  });
});
