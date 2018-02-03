var _truthy = function(val){
    if(!val){
        return false;
    }
    if(val=='0x0000000000000000000000000000000000000000'){
        return false;
    }
    return true;
}
var address_ize = function(key, val, result){
        if(!_truthy(val)){
            return [null, null]
        }
        return [ key, "<a target=new href=https://etherscan.io/address/"+val+">"+val+"</a>"];
    };
var gitcoin_ize = function(key, val, result){
        if(!_truthy(val)){
            return [null, null]
        }
        return [ key, "<a target=new href=https://gitcoin.co/profile/"+val+">@"+val.replace('@','')+"</a>"];
    };
var email_ize = function(key, val, result){
        if(!_truthy(val)){
            return [null, null]
        }
        return [ key, "<a href=mailto:"+val+">"+val+"</a>"];
    };
var hide_if_empty = function(key, val, result){
        if(!_truthy(val)){
            return [null, null]
        }
        return [ key, val];
    };
var unknown_if_empty = function(key, val, result){
        if(!_truthy(val)){
            return [key, 'Unknown']
        }
        return [ key, val];
    };
var link_ize = function(key, val, result){
        if(!_truthy(val)){
            return [null, null]
        }
        return [ key, "<a taget=new href="+val+">"+val+"</a>"];
    };

//rows in the 'about' page
var rows = [
    'avatar_url',
    'title',
    'github_url',
    'value_in_token',
    'value_in_eth',
    'value_in_usdt',
    'web3_created',
    'status',
    'bounty_owner_address',
    'bounty_owner_email',
    'issue_description',
    'bounty_owner_github_username',
    'fulfiller_address',
    'fulfiller_github_username',
    'fulfiller_email',
    'experience_level',
    'project_length',
    'bounty_type',
    'expires_date',
]
var heads = {
    'avatar_url': 'Issue',
    'value_in_token': 'Issue Funding Info',
    'bounty_owner_address': 'Funder',
    'fulfiller_address': 'Submitter',
    'experience_level': 'Meta',
}
var callbacks = {
    'github_url': link_ize,
    'value_in_token': function(key, val, result){
        return [ 'amount', Math.round((parseInt(val) / Math.pow( 10, document.decimals )) * 1000) / 1000 + " " + result['token_name']];
    },
    'avatar_url': function(key, val, result){
        return [ 'avatar', '<a href="/profile/'+result['org_name']+'"><img class=avatar src="'+val+'"></a>'];
    },
    'status': function(key, val, result){
        var ui_status = val;
        if(ui_status=='open'){
            ui_status = '<span style="color: #47913e;">open</span>';
        }
        if(ui_status=='started'){
            ui_status = '<span style="color: #3e00ff;">work started</span>';
        }
        if(ui_status=='submitted'){
            ui_status = '<span style="color: #3e00ff;">work submitted</span>';
        }
        if(ui_status=='done'){
            ui_status = '<span style="color: #0d023b;">done</span>';
        }
        if(ui_status=='cancelled'){
            ui_status = '<span style="color: #f9006c;">cancelled</span>';
        }
        return [ 'status', ui_status];
    },
    'issue_description': function(key, val, result){
        var converter = new showdown.Converter();
        return [ 'issue_description', converter.makeHtml(val)];
    },
    'fulfiller_address': address_ize,
    'bounty_owner_address': address_ize,
    'bounty_owner_email': email_ize,
    'fulfiller_email': email_ize,
    'experience_level': unknown_if_empty,
    'project_length': unknown_if_empty,
    'bounty_type': unknown_if_empty,
    'fulfiller_email': function(key, val, result){
        if(!_truthy(result['fulfiller_address'])){
            $("#fulfiller").addClass('hidden');
        }
        return address_ize(key, val, result);
    },
    'bounty_owner_github_username': gitcoin_ize,
    'fulfiller_github_username': gitcoin_ize,
    'value_in_eth': function(key, val, result){
        if(result['token_name'] == 'ETH' || val == null){
            return [null, null];
        }
        return [ "Amount (ETH)" , Math.round((parseInt(val) / Math.pow( 10, 18 )) * 1000) / 1000];
    },
    'value_in_usdt': function(key, val, result){
        if(val == null){
            return [null, null];
        }
        return [ "Amount_usd" , val];
    },
    'web3_created': function(key, val, result){
        return [ "updated" , timeDifference(new Date(result['now']), new Date(result['created_on']))];
    },
    'expires_date': function(key, val, result){
        var label = "expires";
        expires_date = new Date(val);
        now = new Date(result['now']);
        var response = timeDifference(now, expires_date);
        if( new Date(val) < new Date()){
            label = "expired";
            if(result['is_open']){
                response = "<span title='This issue is past its expiration date, but it is still active.  Check with the submitter to see if they still want to see it fulfilled.'>"+response+"</span>";
            }
        }
        return [ label , response];
    },

}

var isBountyOwner = function(result) {
    var bountyAddress = result['bounty_owner_address']
    return (typeof web3 != 'undefined' && (web3.eth.coinbase == bountyAddress))
}



var pendingChangesWarning = function(issueURL, last_modified_time_remote, now){
    if(typeof web3 == 'undefined'){
        return false;
    }

    console.log("checking this issue for updates:");
    console.log(issueURL);
    //setup callbacks
    var changes_synced_callback = function(){
        document.location.href = document.location.href;
        // check_for_bounty_changed_updates_REST();
    };
    var check_for_bounty_changed_updates_REST = function(){
        var uri = '/api/v0.1/bounties/?github_url='+issueURL;
         $.get(uri, function(results){
            results = sanitizeAPIResults(results);
            var result = results[0];
            // if remote entry has been modified, refresh the page.  if not, try again
            if(typeof result == 'undefined' || result['modified_on'] == last_modified_time_remote){
                setTimeout(check_for_bounty_changed_updates_REST,2000);
            } else {
                changes_synced_callback();
            }
         });
    };

    // Might want to move this to a common location if possible
    var bounty = web3.eth.contract(bounty_abi).at(bounty_address());
    ipfs.ipfsApi = IpfsApi({host: 'ipfs.infura.io', port: '5001', protocol: "https", root:'/api/v0'});
    ipfs.setProvider({ host: 'ipfs.infura.io', port: 5001, protocol: 'https', root:'/api/v0'});

    // Only run this after the transaction is confirmed to be on the blockchain
    var getBountyId = function (callback) {
        // Check if the bountyId already exists for a given issueURL
        var uri = '/api/v0.1/bounties/?github_url='+issueURL
        $.get(uri, function(results) {
            results = sanitizeAPIResults(results);
            var result = results[0];
            if (typeof result != 'undefined' && 'standard_bounties_id' in result) {
                callback(null, result.standard_bounties_id)
            } else {
                //if the bounty id cannot be gotten from the REST API, then pull
                //it from web3
                getBountyIDFromWeb3(callback);
            }
        });
    };

    var getBountyIDFromWeb3 = function(callback){
        var transactionInfo;
        var bountiesLength;
        var bountyId;

        bounty.getNumBounties(function(error, result){
            if (error){
                console.error(error);
                return;
            }
            bountiesLength = parseInt(result, 10);
            console.log('Total bounties length: ' + bountiesLength.toString());
            // Get bounty issuer
            var i = bountiesLength - 1;
            function getBountyLoop (i) {
                bounty.getBounty(i, function(error, result2) {
                    if (error) {
                        console.error(error);
                        return;
                    }
                    issuer = result2[0];
                    // compare issuer to the submitting address
                    if (issuer == document.pendingIssueMetadata['issuer']) {
                        bounty.getBountyData(i, function(error, result3) {
                            if (error) {
                            console.error(error);
                            return;
                            }
                            dataHash = result3;
                            // compare resulting datahash from std bounties to cached dataHash
                            if (dataHash == document.pendingIssueMetadata['dataHash']) {
                                var bountyId = i;
                                console.log('Found matching bountyId: '+ bountyId);
                                callback(null, bountyId);
                            } else {
                                i -= 1;
                                if (i == 0) {
                                    console.log('bountyId not found.')
                                    callback('bountyId not found', 0)
                                } else {
                                getBountyLoop(i);
                                }
                            }
                        })
                    } else {
                        i -= 1;
                        if (i == 0) {
                            console.log('bountyId not found.')
                            callback('bountyId not found', 0)
                        } else {
                        getBountyLoop(i);
                        }
                    }
                })
            }
            getBountyLoop(i)
        })
    };



    var check_for_bounty_changed_updates_web3 = function(){

        // This object contains all information about the bounty pulled from the web3 contract and ipfs.
        // It is then passed to the database to do a sync.
        var allBountyData = {
            bountyId: 0,             // getBountyId() js function.  Bounty Id is calculated iterating through bounty id's and finding a match.
            bountyData: {},          // getBountyData(_bountyId).  This is the data stored in ipfs.
            bounty: {},              // getBounty(_bountyId).  The array retured by web3 contract call.
            fulfillments: {
                'total': 0,          // getNumFulfillments(_bountyId).  The number returned by web3 contract call.
                'fulfillments': [],  // getFulfillment(_bountyId, _fulfillmentId).  Fulfillment information return by web3 contract call.
            },
        };

        // The object will be pushed onto allBountyData.fulfillments.fulfillments
        var allFulfillmentData = {};

        // callFunctionWhenTransactionMined continue to be called, until the transaction receipt is found.
        // Once it is found, it calls the function() defined below.
        callFunctionWhenTransactionMined(document.pendingIssueMetadata['txid'],function(){
            setTimeout(function(){
                getBountyId(function(error, bountyId) {
                   if(bountyId != 0) {
                        bounty.getBountyData(bountyId, function(error, bountyHash) {
                            ipfs.catJson(bountyHash, function(error, bountyData) {
                                bounty.getBounty(bountyId, function(error, bountyResults) {
                                    // Collect all of the bounty data in one place
                                    allBountyData['bountyId'] = bountyId;
                                    allBountyData['bountyData'] = bountyData;

                                    allBountyData['bounty']['issuer'] = bountyResults[0];
                                    allBountyData['bounty']['deadline'] = parseInt(bountyResults[1], 10);
                                    allBountyData['bounty']['fulfillmentAmount'] = parseInt(bountyResults[2], 10);
                                    allBountyData['bounty']['paysTokens'] = bountyResults[3];
                                    allBountyData['bounty']['bountyStage'] = parseInt(bountyResults[4]);
                                    allBountyData['bounty']['balance'] = parseInt(bountyResults[5], 10);

                                    bounty.getNumFulfillments(bountyId, function(error, numFulfillments) {
                                        allBountyData['fulfillments']['total'] = numFulfillments;
                                        if (numFulfillments > 0) {
                                            // Just get latest fullfillment data
                                            // TODO:  Add support for multilple fulfillments
                                            var fulfillmentId = numFulfillments - 1;
                                            bounty.getFulfillment(bountyId, fulfillmentId, function(error, fulfillment) {
                                                ipfs.catJson(fulfillment[2], function(error, fulfillmentData) {
                                                    allFulfillmentData = fulfillmentData;
                                                    allFulfillmentData['accepted'] = fulfillment[0];

                                                    // Push the fulfillment onto the array
                                                    allBountyData.fulfillments.fulfillments.push(allFulfillmentData);

                                                    sync_web3(document.issueURL, JSON.stringify(allBountyData), changes_synced_callback);
                                                    console.log('success syncing with web3');
                                                })
                                            });
                                        } else {
                                            sync_web3(document.issueURL, JSON.stringify(allBountyData), changes_synced_callback);
                                            console.log('success syncing with web3');
                                        }
                                    })
                                });
                            });
                        });


                    } else {
                        // console.error(result);
                        var link_url = etherscan_tx_url(document.pendingIssueMetadata['txid']);
                        _alert("<a target=new href='"+link_url+"'>There was an error executing the transaction.</a>  Please <a href='#' onclick='window.history.back();'>try again</a> with a higher gas value.  ")
                    }
                });
            },1000)
        });
    };

    var showWarningMessage = function () {

        if (typeof document.pendingIssueMetadata['txid'] != 'undefined' && document.pendingIssueMetadata['txid'].indexOf('0x') != -1) {
            clearInterval(interval);
            var link_url = etherscan_tx_url(document.pendingIssueMetadata['txid']);
            $('#pending_changes').attr("href", link_url);
            $('#transaction_url').attr("href", link_url);
        }

        $("#bounty_details").hide();
        $("#bounty_detail").hide();

        $(".transaction-status").show();
        $(".waiting_room_entertainment").show();

        var radioButtons = $(".sidebar_search input");

        for (var i = radioButtons.length - 1; i >= 0; i--) {
            radioButtons[i].disabled = true;
        }

        var secondsBetweenQuoteChanges = 30;
        waitingRoomEntertainment();
        var interval = setInterval(waitingRoomEntertainment, secondsBetweenQuoteChanges * 1000);
    };

    // This part decides if a warning banner should be displayed
    var should_display_warning = false;
    if (document.pendingIssueMetadata) {  // localStorage[issueURL] is the "local timestamp"
        //local warning
        var local_delta = parseInt(timestamp() - document.pendingIssueMetadata['timestamp']);
        var is_changing_local_recent = local_delta < (60 * 60); // less than one hour

        //remote warning
        var remote_delta = (new Date(now) - new Date(last_modified_time_remote)) / 1000;
        var is_changing_remote_recent = remote_delta < (60 * 60); // less than one minute

        should_display_warning = !last_modified_time_remote || ((is_changing_local_recent) && (remote_delta > local_delta));

        if (should_display_warning) {
            showWarningMessage();
            showLoading();
            check_for_bounty_changed_updates_web3();
        }
    }

    return should_display_warning;
};

window.addEventListener('load', function() {

    var build_detail_page = function(result){
        //setup
        var decimals = 18;
        var related_token_details = tokenAddressToDetails(result['token_address'])
        if(related_token_details && related_token_details.decimals){
            decimals = related_token_details.decimals;
        }
        $("#bounty_details").css('display','flex');
        document.decimals = decimals;

        // title
        result['title'] = result['title'] ? result['title'] : result['github_url'];
        result['title'] = result['network'] != 'mainnet' ? "(" + result['network'] + ") " + result['title'] : result['title'];
        $('.title').html("Funded Issue Details: " + result['title']);

        //insert table onto page
        for(var j=0; j< rows.length; j++){
            var key = rows[j];
            var head = null;
            var val = result[key];
            if(heads[key]){
                head = heads[key];
            }
            if(callbacks[key]){
                _result = callbacks[key](key, val, result);
                val = _result[1];
            }
            var entry = {
                'head': head,
                'key': key,
                'val': val,
            }
            var id = '#' + key;
            if($(id).length){
                $(id).html(val);
            }
        }        
    }

    var do_actions = function(result){
        // Find interest information
        pull_interest_list(result['pk'], function(is_interested){

        //actions
        var actions = [];
        if(result['github_url'].substring(0,4) == 'http'){

            var github_url = result['github_url'];
            // hack to get around the renamed repo for piper's work.  can't change the data layer since blockchain is immutable
            github_url = github_url.replace('pipermerriam/web3.py','ethereum/web3.py');

            if(result['github_comments']){
                var entry_comment = {
                  href: github_url,
                  text: result['github_comments'],
                  target: 'new',
                  parent: 'right_actions',
                  color: 'github-comment'
                };
                actions.push(entry_comment);
            }

            var entry = {
                href: github_url,
                text: 'View on Github',
                target: 'new',
                parent: 'right_actions',
                color: 'darkBlue',
                title: 'Github is where the issue scope lives.  Its also a great place to collaborate with, and get to know, other developers (and sometimes even the repo maintainer themselves!).'
            }
            actions.push(entry);
        }

        if(result['status'] != 'done' && result['status'] != 'cancelled'){
            var enabled = isBountyOwner(result);
            var entry = {
                href: '/funding/kill?source='+result['github_url'],
                text: 'Kill Bounty',
                parent: 'right_actions',
                color: enabled ? 'darkBlue' : 'darkGrey',
                extraClass: enabled ? '' : 'disabled',
                title: enabled ? 'This will kill the bounty and return the funds.' : 'Can only be performed if you are the funder.',
            }
            actions.push(entry);
        }

        var enabled = !isBountyOwner(result);
        if(result['status']=='open' || result['status']=='started' ){
            var interestEntry = {
                href: is_interested ? '/uninterested' : '/interested',
                text: is_interested ? 'Stop Work' : 'Start Work',
                parent: 'right_actions',
                color: enabled ? 'darkBlue' : 'darkGrey',
                extraClass: enabled ? '' : 'disabled',
                title: enabled ? 'Start Work in an issue to let the issue funder know that youre interested in working with them.  Use this functionality when you START work.  Please leave a comment for the bounty submitter to let them know you are interested in working with them after you start work.' : 'Can only be performed if you are not the funder.',
            }
            actions.push(interestEntry);

            var entry = {
                href: '/funding/fulfill?source='+result['github_url'],
                text: 'Submit Work',
                parent: 'right_actions',
                color: enabled ? 'darkBlue' : 'darkGrey',
                extraClass: enabled ? '' : 'disabled',
                title: enabled ? 'Use Submit Work when you FINISH work on a bounty.   Use Start Work when you START work.' : 'Can only be performed if you are not the funder.',
            }
            actions.push(entry);
        }

        var is_expired = result['status']=='expired' || (new Date(result['now']) > new Date(result['expires_date']));

        if(result['status']=='submitted' ){
            var enabled = isBountyOwner(result);
            var entry = {
                href: '/funding/process?source='+result['github_url'],
                text: 'Accept Submission',
                parent: 'right_actions',
                color: enabled ? 'darkBlue' : 'darkGrey',
                extraClass: enabled ? '' : 'disabled',
                title: enabled ? 'This will payout the bounty to the fulfiller.' : 'Can only be performed if you are the funder.',

            }
            actions.push(entry);
        }
        render_actions(actions);

        });
    }

    var render_actions = function(actions){
        for(var l=0; l< actions.length; l++){
            var target = actions[l]['parent'];
            var tmpl = $.templates("#action");
            var html = tmpl.render(actions[l]);
            $("#"+target).append(html);
        };      
    }

    setTimeout(function(){
        document.issueURL = getParam('url');
        if(localStorage[document.issueURL]){
            document.pendingIssueMetadata = JSON.parse(localStorage[document.issueURL]);
        }

        $("#submitsolicitation a").attr('href','/funding/new/?source=' + document.issueURL)
        var uri = '/api/v0.1/bounties/?';
        $.get(uri, function(results){
            results = sanitizeAPIResults(results);
            var nonefound = true;
            // potentially make this a lot faster by only pulling the specific issue required
            for(var i = 0; i<results.length; i++){
                var result = results[i];
                // if the result from the database matches the one in question..
                if(normalizeURL(result['github_url']) == normalizeURL(document.issueURL)){

                    nonefound = false;

                    build_detail_page(result);
                    do_actions(result);

                    //cleanup
                    document.result = result;
                    pendingChangesWarning(document.issueURL, result['created_on'], result['now']);
                    return;
                }
            }

            if (nonefound) {
                $(".nonefound").css('display','block');
                $("#primary_view").css('display','none');
                pendingChangesWarning(document.issueURL);
            }
        }).fail(function(){
            _alert('got an error. please try again, or contact support@gitcoin.co');
                $("#primary_view").css('display','none');
        }).always(function(){
            $('.loading').css('display', 'none');
        });

    },100);
});


$(document).ready(function(){
    $("body").delegate('a[href="/watch"], a[href="/unwatch"]', 'click', function(e){
        e.preventDefault();
        if($(this).attr('href') == '/watch'){
            $(this).attr('href','/unwatch');
            $(this).find('span').text('Unwatch');
        } else {
            $(this).attr('href','/watch');
            $(this).find('span').text('Watch');
        }
    });
    $("body").delegate('a[href="/interested"], a[href="/uninterested"]', 'click', function (e) {
        e.preventDefault();
        if ($(this).attr('href') == '/interested') {
            $(this).attr('href', '/uninterested');
            $(this).find('span').text('Stop Work');
            add_interest(document.result['pk']);
        } else {
            $(this).attr('href', '/interested');
            $(this).find('span').text('Start Work');
            remove_interest(document.result['pk']);
        }
    });
})
