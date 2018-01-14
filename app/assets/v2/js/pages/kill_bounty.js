
window.onload = function(){
    //a little time for web3 injection
    setTimeout(function(){
        var account = web3.eth.accounts[0];

        if (typeof localStorage['acceptTOS'] !='undefined' && localStorage['acceptTOS']){
            $('input[name=terms]').attr('checked','checked');
        }
        if(getParam('source')){
            $('input[name=issueURL]').val(getParam('source'));
        }

        var estimateGas = function(issueURL, success_callback, failure_calllback, final_callback){
            var bounty = web3.eth.contract(bounty_abi).at(bounty_address());
            $("#gasLimit").addClass('loading');
            bounty.clawbackExpiredBounty.estimateGas(
                issueURL, 
                function(errors,result){
                    $("#gasLimit").removeClass('loading');
                    var is_issue_taken = typeof result == 'undefined' || result > 403207;
                    if(errors || is_issue_taken){
                        failure_calllback(errors);
                        return;
                    }
                    var gas = Math.round(result * gasMultiplier);
                    var gasLimit = Math.round(gas * gasLimitMultiplier);
                    success_callback(gas, gasLimit, final_callback);
            });
        };
        //updates recommended metamask settings
        var updateInlineGasEstimate = function(){
            var issueURL = $('input[name=issueURL]').val();
            var success_callback = function(gas, gasLimit, _){
                $("#gasLimit").val(gas);
                update_metamask_conf_time_and_cost_estimate();
            };
            var failure_callback = function(errors){
                $("#gasLimit").val('Unknown');
                update_metamask_conf_time_and_cost_estimate();
            };
            var final_callback = function(){};
            //estimateGas(issueURL, success_callback, failure_callback, final_callback);
            success_callback(86936,86936,'');
        };
        setTimeout(function(){
            updateInlineGasEstimate();
        },100);
        $('input').change(updateInlineGasEstimate);
        $('#gasPrice').keyup(update_metamask_conf_time_and_cost_estimate);

        $('#submitBounty').click(function(e){
            mixpanel.track("Clawback Bounty Clicked", {});
            loading_button($('#submitBounty'));
            e.preventDefault();
            var issueURL = $('input[name=issueURL]').val();

            var isError = false;
            if($('#terms:checked').length == 0){
                _alert({ message: "Please accept the terms of service." });
                isError = true;
            } else {
                localStorage['acceptTOS'] = true;
            }
            if(issueURL == ''){
                _alert({ message: "Please enter a issue URL." });
                isError = true;
            }
            if(isError){
                unloading_button($('#submitBounty'));
                return;
            }

            var bounty = web3.eth.contract(bounty_abi).at(bounty_address());

            var apiCallback = function(results, status){
                if(status != "success"){
                    mixpanel.track("Kill Bounty Error", {step: 'apiCallback', error: error});
                    _alert({ message: "Could not get bounty details" });
                    console.error(error);
                    unloading_button($('.submitBounty'));
                    return;
                } else {
                    results = sanitizeAPIResults(results);
                    result = results[0];

                    var bountyAmount = parseInt(result['value_in_token'], 10); 
                    var fromAddress = result['bounty_owner_address'];
                    var claimeeAddress = result['claimeee_address'];
                    var open = result['is_open'];
                    var initialized = true;
                    var bountyId = result['standard_bounties_id'];

                    var errormsg = undefined;
                    if(bountyAmount == 0 || open == false || initialized == false){
                        errormsg = "No active funded issue found at this address.  Are you sure this is an active funded issue?";
                    } 
                    if(fromAddress != web3.eth.coinbase){
                        errormsg = "Only the address that submitted this funded issue may kill the bounty.";
                    }

                    if(errormsg){
                        _alert({ message: errormsg });
                        unloading_button($('#submitBounty'));
                        return;
                    }

                    var final_callback = function(error, result){
                        var next = function(){
                            localStorage['txid'] = result;
                            updates = {
                                is_open: false,  // Close out the bounty in the database
                                idx_status: 'dead',
                            }
                            sync_web3(issueURL, JSON.stringify(updates));
                            localStorage[issueURL] = timestamp();
                            add_to_watch_list(issueURL);
                            _alert({ message: "Kill bounty submitted to web3." },'info');
                            setTimeout(function(){
                                mixpanel.track("Kill Bounty Success", {});
                                document.location.href= "/funding/details?url="+issueURL;
                            },1000);

                        };
                        if(error){
                            mixpanel.track("Kill Bounty Error", {step: 'final_callback', error: error});
                            console.error("err", error);
                            _alert({ message: "There was an error" });
                            unloading_button($('#submitBounty'));
                        } else {
                            next();
                        }
                    };

                    setTimeout(function(){
                        var failure_calllback = function(errors){
                            _alert({ message: "This issue cannot be clawed back.  Please leave a comment <a href=https://github.com/gitcoinco/web/issues/169>here</a> if you need help." });
                            mixpanel.track("Claim Bounty Error", {step: 'estimateGas', error: errors});
                            unloading_button($('#submitBounty'));
                            return;                            
                        }
                        var success_callback = function(gas, gasLimit, final_callback){
                            var bounty = web3.eth.contract(bounty_abi).at(bounty_address());
                            bounty.clawbackExpiredBounty.sendTransaction(issueURL, 
                                {
                                    from : account,
                                    gas:web3.toHex(gas), 
                                    gasLimit: web3.toHex(gasLimit), 
                                    gasPrice:web3.toHex($("#gasPrice").val() * 10**9), 
                                }, 
                            final_callback);
                        };
                        // estimateGas(issueURL, success_callback, failure_calllback, final_callback);
                    },100);
                    bounty.killBounty(bountyId, final_callback);
                    e.preventDefault();
                }
            };
            // Get bountyId from the database
            var uri = '/api/v0.1/bounties?github_url='+issueURL;
            $.get(uri, apiCallback); 
            e.preventDefault();
        });
    },100);

};
