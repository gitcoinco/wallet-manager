// security token
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

// grab our profile_id
const profile_id = JSON.parse(document.getElementById('user_id').textContent);

// DOMContentLoaded
document.addEventListener('DOMContentLoaded', function() {

  updateInterface('init');

  // bann & forward zerotoken-claimers
  let total_claimable_gtc = document.getElementById('total_claimable_gtc');

  if (total_claimable_gtc.dataset.total_claimable_gtc == 0) {
    updateInterface('zerotokens');
  }

  window.addEventListener('dataWalletReady', function(e) {

    // show selectedAccount in textarea claim_address
    const claim_address = document.getElementById('claim_address');

    claim_address.value = selectedAccount;

    // grab claim status from token dist contract
    async function getClaimStatus(profile_id) {
      is_claimed = await isClaimed(profile_id);
      return is_claimed;
    }

    let has_claimed = getClaimStatus(profile_id);

    has_claimed.then(function(claim_result) {
      if (claim_result) {
        window.location = '/quadraticlands/mission/receive/outro';
      }
    });
    var textarea_delegate_address = document.getElementById('delegate_address');

    // if user did mission/use/delegate he set an address from a senator into his local storage.
    // if he wana delegate to a senator on claiming - we use this address.
    // else we just selfdelegate his current address.
    var stewardsaddress = localStorage.getItem('stewardsaddress');

    if (stewardsaddress) {
      textarea_delegate_address.value = stewardsaddress;
      console.debug('found a steward delegate to : ' + stewardsaddress);
    } else {
      textarea_delegate_address.value = selectedAccount;
      console.debug('no steward found, selfdelegate to : ' + selectedAccount);
    }
  }, false);

  // as a user can still edit the delegate address textadrea
  // heres a little clientside validation on this textarea
  // that hides the claim button when theres a bad eth address in
  delegate_address_validation = document.getElementById('delegate_address');

  delegate_address_validation.addEventListener('input', () => {

    if (web3.utils.checkAddressChecksum(delegate_address_validation.value) == true) {
      // valid eth address
      console.debug('input : delegate address valid');
      document.getElementById('divClaimButton').classList.remove('hide');
      delegate_address_validation.classList.remove('warning');
    } else {
      // no valid eth address
      console.debug('input : delegate address not valid');
      document.getElementById('divClaimButton').classList.add('hide');
      delegate_address_validation.classList.add('warning');
    }

  });

  $(document).on('click', '#beginClaim', (event) => {

    if (is_impersonate) {
      return console.error('Claim cannot be triggered by impersonated user');
    }

    console.debug('BEGIN CLAIM');

    // confirm we have a working web3 connection if not, return error
    try {
      const network = checkWeb3();
    } catch (error) {
      return console.error('Please confirm you have a wallet connected!!');
    }

    /**
      * POST to claim endpoint
      * provided active account/address (claim address) & delegate address
      * returns signed claim message data
    * */

    // read delegate_address from textarea
    var delegate_address = document.getElementById('delegate_address').value;

    console.debug('DELEGATE TO ', delegate_address);

    var getClaimData = fetchData('/quadraticlands/claim', 'POST', {
      'address': selectedAccount,
      'delegate': delegate_address
    }, { 'X-CSRFToken': csrftoken });

    $.when(getClaimData).then((response, status, statusCode) => {
      // setup & send our contract call
      setupGTCTokenClaim(response);
    }).catch((error) => {
      console.error('Unable to fetch signed claim: ', error.status);
      updateInterface('esms_down');
    });
  });
});


// setupGTCTokenClaim
async function setupGTCTokenClaim(emss_response) {

  const user_id = emss_response.user_id;
  const user_amount = emss_response.user_amount;
  const user_address_cleaned = web3.utils.toChecksumAddress(emss_response['user_address'].replace(/\"/g, ''));
  const delegate_address_cleaned = web3.utils.toChecksumAddress(emss_response['delegate_address'].replace(/\"/g, ''));
  const eth_signed_message_hash_hex = emss_response.eth_signed_message_hash_hex.replace(/\"/g, '');
  const eth_signed_signature_hex = emss_response.eth_signed_signature_hex.replace(/\"/g, '');
  const leaf = emss_response.leaf.replace(/\"/g, '');
  const proof = emss_response.proof;

  try {

    const tokenDistributor = await new web3.eth.Contract(
      token_distributor_abi,
      token_distributor_address()
    );

    const claimGTCtokens = () => {

      tokenDistributor.methods
        .claimTokens(user_id, user_address_cleaned, web3.utils.toWei(user_amount, 'ether'), delegate_address_cleaned, eth_signed_message_hash_hex, eth_signed_signature_hex, proof, leaf)
        .send({ from: selectedAccount, gasLimit: '300000' })
        .on('transactionHash', async function(transactionHash) {

          // update interface to the pending view ( claiming )
          updateInterface('pending', transactionHash);
          console.debug('TRANSACTION HASH - PENDING: ', transactionHash);
        })
        .on('receipt', receipt => {
          console.debug('RECEIPT - receipt');
        })
        .on('confirmation', (confirmationNumber, receipt) => {
          console.log('ON CONFIRMATION');
          if (confirmationNumber >= 0 && confirmationNumber < 6) {
            // update interface to the success view ( claimed )
            updateInterface('success');
            console.debug('CONFIRMATION >= 0');
          }
        })
        .on('error', (error) => {
          updateInterface('error');
          console.error('Error-2 on TX send:', error);
        });
    };

    claimGTCtokens();
  } catch (error) {
    console.error('Error-1 on TX send:', error);
  }

}

// checkNetwork
function checkNetwork() {
  const supportedNetworks = [ 'rinkeby', 'mainnet' ];

  if (!supportedNetworks.includes(document.web3network)) {
    flashMessage('Unsupported network', 5000);
    throw new Error;
  }
  return document.web3network;
}

// checkWeb3
function checkWeb3() {
  if (!web3) {
    flashMessage('Please connect a wallet', 5000);
    throw new Error;
  }
  return checkNetwork();
}

// DYNAMIC USER INTERFACE
// status = init, pending, success, error, esms_down
function updateInterface(status = 'init', transactionHash = '') {

  // main views
  const view_claim = document.getElementById('claim');
  const view_claiming = document.getElementById('claiming');
  const view_claimed = document.getElementById('claimed');
  const view_error = document.getElementById('error');
  const esms_down = document.getElementById('esms_down');
  const zerotokens = document.getElementById('zerotokens');

  const blockExplorerName = 'Etherscan';

  // dynamic bottom bar
  const divClaimButton = document.getElementById('divClaimButton');
  const divClaimingSpinner = document.getElementById('divClaimingSpinner');
  const divClaimedButton = document.getElementById('divClaimedButton');

  // transaction links
  const transaction_link_pending = document.getElementById('transaction_link_pending');
  const transaction_link_success = document.getElementById('transaction_link_success');
  const transaction_link_error = document.getElementById('transaction_link_error');

  if (status == 'init') {
    // switch view to
    view_claim.classList.remove('hide');
    view_claiming.classList.add('hide');
    view_claimed.classList.add('hide');
    view_error.classList.add('hide');
    esms_down.classList.add('hide');
    zerotokens.classList.add('hide');

    // dynamic bottom bar
    divClaimButton.classList.remove('hide');
    divClaimingSpinner.classList.add('hide');
    divClaimedButton.classList.add('hide');

    // particles
    window.kinetics.set({
      particles: {
        sizes: { min: 100, max: 200 }, rotate: { speed: 0.2 },
        mode: { type: 'linear', boundery: 'endless', speed: '1' }
      }
    });


  }

  if (status == 'pending') {
    // switch view to
    view_claim.classList.add('hide');
    view_claiming.classList.remove('hide');
    view_claimed.classList.add('hide');
    esms_down.classList.add('hide');
    view_error.classList.add('hide');
    zerotokens.classList.add('hide');

    // dynamic bottom bar
    divClaimButton.classList.add('hide');
    divClaimingSpinner.classList.remove('hide');
    divClaimedButton.classList.add('hide');

    // particles
    window.kinetics.set({
      particles: {
        sizes: { min: 10, max: 20 }, rotate: { speed: 5 },
        mode: { type: 'wind-from-right', boundery: 'endless', speed: '20' }
      }
    });


    // build an etherscan link for this transaction
    tx_link = get_etherscan_url(transactionHash, document.web3network);
    link = "<a target='_blank' href='" + tx_link + "'>" + blockExplorerName + '</a>';
    transaction_link_pending.innerHTML = link;
    transaction_link_success.innerHTML = link;
    transaction_link_error.innerHTML = link;

    // notification
    flashMessage('Your claim has been broadcast to the network!', 5000);
  }

  if (status == 'success') {
    // switch view to
    view_claim.classList.add('hide');
    view_claiming.classList.add('hide');
    view_claimed.classList.remove('hide');
    esms_down.classList.add('hide');
    view_error.classList.add('hide');
    zerotokens.classList.add('hide');

    // dynamic bottom bar
    divClaimButton.classList.add('hide');
    divClaimingSpinner.classList.add('hide');
    divClaimedButton.classList.remove('hide');

    // particles
    window.kinetics.set({
      particles: {
        sizes: { min: 10, max: 20 }, rotate: { speed: 3 },
        mode: { type: 'linear', boundery: 'emitter', speed: '20' }
      }
    });

    // notification
    flashMessage('Transaction Confirmed', 5000);
  }
  if (status == 'error') {
    // switch view to
    view_claim.classList.add('hide');
    view_claiming.classList.add('hide');
    view_claimed.classList.add('hide');
    esms_down.classList.add('hide');
    view_error.classList.remove('hide');
    zerotokens.classList.add('hide');

    // dynamic bottom bar
    divClaimButton.classList.add('hide');
    divClaimingSpinner.classList.add('hide');
    divClaimedButton.classList.add('hide');

    // particles
    window.kinetics.set({
      particles: {
        sizes: { min: 5, max: 10 }, rotate: { speed: 3 },
        mode: { type: 'space', boundery: 'endless', speed: '10' }
      }
    });

    // notification
    flashMessage('Error', 5000);
  }

  if (status == 'esms_down') {
    // switch view to
    view_claim.classList.add('hide');
    view_claiming.classList.add('hide');
    view_claimed.classList.add('hide');
    view_error.classList.add('hide');
    esms_down.classList.remove('hide');
    zerotokens.classList.add('hide');

    // dynamic bottom bar
    divClaimButton.classList.add('hide');
    divClaimingSpinner.classList.add('hide');
    divClaimedButton.classList.add('hide');

    // particles
    window.kinetics.set({
      particles: {
        sizes: { min: 5, max: 10 }, rotate: { speed: 3 },
        mode: { type: 'space', boundery: 'endless', speed: '10' }
      }
    });

    // notification
    flashMessage('Error', 5000);
  }


  if (status == 'zerotokens') {
    // switch view to
    view_claim.classList.add('hide');
    view_claiming.classList.add('hide');
    view_claimed.classList.add('hide');
    view_error.classList.add('hide');
    esms_down.classList.add('hide');
    zerotokens.classList.remove('hide');

    // dynamic bottom bar
    divClaimButton.classList.add('hide');
    divClaimingSpinner.classList.add('hide');
    divClaimedButton.classList.add('hide');

    // particles
    window.kinetics.set({
      particles: {
        sizes: { min: 5, max: 10 }, rotate: { speed: 3 },
        mode: { type: 'space', boundery: 'endless', speed: '10' }
      }
    });

  }


}
