/* eslint-disable no-console */
window.onload = function() {

  setTimeout(function() {
    $('loading').style.display = 'none';

    if (coin_status === 'INITIAL') {
      $('send_eth').style.display = 'block';
    } else if (coin_status === 'PENDING') {
      $('send_eth_done').style.display = 'block';
      $('colo_txid').innerHTML = "<a target=new href='https://" + etherscanDomain() + '/tx/' + colo_txid + "'>See your transaction on the blockchain here</a>";
    }
  }, 500);
};

function redeemCoin() {
  mixpanel.track('Redeem Coin Click', {});
  metaMaskWarning();

  var forwarding_address = $('forwarding_address').value.trim();

  // Check for valid address
  isValidForwardingAddress = forwarding_address.indexOf('0x') != -1;
  if (!forwarding_address || !isValidForwardingAddress) {
    _alert('Not a valid forwarding address.');
    return;
  }

  var sendEthInnerHTML = $('send_eth').innerHTML;

  $('send_eth').innerHTML = "<img src='/static/yge/images/loading_v2.gif' style='max-width: 70px; max-height: 70px;'><br><h4>Submitting to the blockchain...</h4>";

  fetch(window.location.href, {
    method: 'POST',
    body: JSON.stringify({
      address: forwarding_address
    })
  })
    .then(
      function(response) {
        response.json().then(function(data) {
          if (data.status === 'OK') {
            mixpanel.track('Redeem COLO Coin Success', {});
            startConfetti();
            $('send_eth').innerHTML = "<h1>Success 🚀!</h1> <a target=new href='https://" + etherscanDomain() + '/tx/' + data.message + "'>See your transaction on the blockchain here</a>.<br><br><span id=mighttake>It might take a few minutes to sync, depending upon: <br> - network congestion<br> - network fees that sender allocated to transaction<br></span><br><a id='' class='button' href='/'>⬅ Check out Gitcoin.co</a>";
          } else {
            if (data.message.indexOf('Address has an invalid EIP checksum') !== -1) {
              _alert('Please enter a valid checksum address.');
            } else {
              _alert(data.message);
            }

            $('send_eth').innerHTML = sendEthInnerHTML;
            mixpanel.track('Redeem COLO Coin Error', {
              error: data.message
            });
          }
        });
      }
    )
    .catch(function(err) {
      console.log('Fetch Error :-S', err);
    });
}
