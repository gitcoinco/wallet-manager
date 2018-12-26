/* eslint-disable no-console */

$(document).ready(function() {

  if (localStorage['grants_quickstart_disable'] !== 'true') {
    window.location = document.location.origin + '/grants/quickstart';
  }

  web3.eth.getAccounts(function(err, accounts) {
    $('#input-admin_address').val(accounts[0]);
    $('#contract_owner_address').val(accounts[0]);
  });


  $('#js-token').append("<option value='0x0000000000000000000000000000000000000000'>Any Token");

  userSearch('.team_members');

  $('#img-project').on('change', function() {
    if (this.files && this.files[0]) {
      if (exceedFileSize(this.files[0])) {
        _alert({ message: 'Grant Image should not exceed 4MB' }, 'error');
        return;
      }

      let reader = new FileReader();

      reader.onload = function(e) {
        $('#preview').attr('src', e.target.result);
        $('#preview').css('width', '100%');
        $('#js-drop span').hide();
        $('#js-drop input').css('visible', 'invisible');
        $('#js-drop').css('padding', 0);
      };
      reader.readAsDataURL(this.files[0]);
    }
  });

  $('.js-select2, #frequency_unit').each(function() {
    $(this).select2();
  });

  $('#create-grant').validate({
    submitHandler: function(form) {
      var data = {};
      var disabled = $(form)
        .find(':input:disabled')
        .removeAttr('disabled');

      $.each($(form).serializeArray(), function() {
        data[this.name] = this.value;
      });

      $('#token_symbol').val($('#js-token option:selected').text());

      if (document.web3network) {
        $('#network').val(document.web3network);
      }

      // Begin New Deploy Subscription Contract
      let SubscriptionContract = new web3.eth.Contract(compiledSubscription.abi);

      // These args are baseline requirements for the contract set by the sender. Will set most to zero to abstract complexity from user.
      let args = [
        // admin_address
        web3.utils.toChecksumAddress(data.admin_address),
        // required token
        web3.utils.toChecksumAddress(data.denomination),
        // required tokenAmount
        web3.utils.toTwosComplement(0),
        // data.frequency
        web3.utils.toTwosComplement(0),
        // data.gas_price
        web3.utils.toTwosComplement(0),
        // contract version
        web3.utils.toTwosComplement(0)
      ];

      web3.eth.getAccounts(function(err, accounts) {
        web3.eth.net.getId(function(err, network) {
          SubscriptionContract.deploy({
            data: compiledSubscription.bytecode,
            arguments: args
          }).send({
            from: accounts[0],
            gas: 3000000,
            gasPrice: web3.utils.toHex($('#gasPrice').val() * Math.pow(10, 9))
          }).on('error', function(error) {
            console.log('1', error);
          }).on('transactionHash', function(transactionHash) {
            console.log('2', transactionHash);
            $('#transaction_hash').val(transactionHash);
            const linkURL = etherscan_tx_url(transactionHash);

            document.issueURL = linkURL;
            $('#transaction_url').attr('href', linkURL);
            enableWaitState('#new-grant');

            var callFunctionWhenTransactionMined = function(transactionHash) {
              web3.eth.getTransactionReceipt(transactionHash, function(error, result) {
                if (result) {
                  $('#contract_address').val(result.contractAddress);
                  $.each($(form).serializeArray(), function() {
                    data[this.name] = this.value;
                  });
                  form.submit();
                } else {
                  setTimeout(function() {
                    callFunctionWhenTransactionMined(transactionHash);
                  }, 1000);
                }
              });
            };

            callFunctionWhenTransactionMined(transactionHash);
          });
          // .on('receipt', function(receipt) {
          //   $('#contract_address').val(receipt.contractAddress);
          // }).then(function(contractInstance) {
          //   console.log(contractInstance);
          //   $.each($(form).serializeArray(), function() {
          //     data[this.name] = this.value;
          //   });
          //   console.log(data);
          //   // form.submit();
          // });
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
    });

    $('#js-token').select2();
    $("#js-token option[value='0x0000000000000000000000000000000000000000']").remove();
    $('#js-token').append("<option value='0x0000000000000000000000000000000000000000' selected='selected'>Any Token");
  });

  $('.select2-selection__rendered').removeAttr('title');
});

const exceedFileSize = (file, size = 4000000) => {
  if (file.size > size)
    return true;
  return false;
};
