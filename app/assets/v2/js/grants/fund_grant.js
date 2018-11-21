/* eslint-disable no-console */
$(document).ready(function() {

  $('#period').select2();

  $('.js-select2').each(function() {
    $(this).select2();
  });

  // alert("Just so you know, you will perform two actions in MetaMask on this page!")

  $('#js-fundGrant').validate({
    submitHandler: function(form) {
      var data = {};

      $.each($(form).serializeArray(), function() {
        data[this.name] = this.value;
      });

      $('#token_symbol').val($('#js-token option:selected').text());

      let realPeriodSeconds = 0;

      if (data.frequency) {

        // translate timeAmount&timeType to requiredPeriodSeconds
        let periodSeconds = data.frequency;

        if (data.frequency_unit == 'days') {
          periodSeconds *= 86400;
        } else if (data.frequency_unit == 'months') {
          periodSeconds *= 2592000;
        }
        if (periodSeconds) {
          realPeriodSeconds = periodSeconds;
        }
      }

      let deployedSubscription = new web3.eth.Contract(compiledSubscription.abi, data.contract_address);

      if (data.token_address != '0x0000000000000000000000000000000000000000') {
        let deployedToken = new web3.eth.Contract(compiledToken.abi, data.token_address);
      } else {
        let deployedToken = new web3.eth.Contract(compiledToken.abi, data.denomination);
      }

      deployedToken.methods.decimals().call(function(err, decimals) {

        let realApproval = Number((data.approve * 10 ** decimals) * data.amount_per_period);

        let realTokenAmount = Number(data.amount_per_period * 10 ** decimals);

        // gas price in gwei
        let realGasPrice = Number(4 * 10 ** 9);

        $('#gas_price').val(4);


        web3.eth.getAccounts(function(err, accounts) {

          $('#contributor_address').val(accounts[0]);

          deployedToken.methods.approve(data.contract_address, web3.utils.toTwosComplement(realApproval)).send({from: accounts[0], gasPrice: 4000000000}, function(err, result) {

            // Should add approval transactions to transaction history

            deployedSubscription.methods.extraNonce(accounts[0]).call(function(err, nonce) {

              nonce = parseInt(nonce) + 1;

              const parts = [
                // subscriber address
                accounts[0],
                // admin_address
                data.admin_address,
                // token denomination / address
                data.denomination,
                // data.amount_per_period
                web3.utils.toTwosComplement(realTokenAmount),
                // data.period_seconds
                web3.utils.toTwosComplement(realPeriodSeconds),
                // data.gas_price
                web3.utils.toTwosComplement(realGasPrice),
                // nonce
                web3.utils.toTwosComplement(nonce)
              ];

              console.log('realTokenAmount', realTokenAmount);
              console.log('realPeriodSeconds', realPeriodSeconds);
              console.log('realGasPrice', realGasPrice);
              console.log('parts', parts);

              deployedSubscription.methods.getSubscriptionHash(...parts).call(function(err, subscriptionHash) {

                $('#subscription_hash').val(subscriptionHash);


                web3.eth.personal.sign('' + subscriptionHash, accounts[0], function(err, signature) {

                  $('#signature').val(signature);

                  let postData = {
                    subscriptionContract: data.contract_address,
                    parts: parts,
                    subscriptionHash: subscriptionHash,
                    signature: signature
                  };

                  console.log('postData', postData);

                  $('#real_period_seconds').val(realPeriodSeconds);

                  $.each($(form).serializeArray(), function() {
                    data[this.name] = this.value;
                  });

                  console.log('data', data);

                  form.submit();

                  fetch('http://localhost:10003/saveSubscription', {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                      postData
                    })
                  }).then((response)=>{
                    console.log('TX RESULT', response);

                    $.each($(form).serializeArray(), function() {
                      data[this.name] = this.value;
                    });

                    data.frequency = realPeriodSeconds;

                    console.log('data', data);

                    form.submit();

                  })
                    .catch((error)=>{
                      console.log(error);
                    });
                });
              });
            });
          });
        });
      });
    }
  });

  waitforWeb3(function() {
    tokens(document.web3network).forEach(function(ele) {
      let option = document.createElement('option');

      option.text = ele.name;
      option.value = ele.addr;

      $('#js-token').append($('<option>', {
        value: ele.addr,
        text: ele.name
      }));

      $("#js-token option[value='0x0000000000000000000000000000000000000000']").remove();
    });
    $('#js-token').select2();
  });
});
