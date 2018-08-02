/* eslint-disable no-loop-func */

var sidebar_keys = [
  'experience_level',
  'project_length',
  'bounty_type',
  'bounty_filter',
  'network',
  'idx_status',
  'tech_stack',
  'project_type',
  'permission_type',
  'misc'
];

var localStorage;
var dashboard = {};

dashboard.limit = 10;
dashboard.draw_distance = 5;
dashboard.bounty_offset = 0;
dashboard.finished_appending = false;
try {
  localStorage = window.localStorage;
} catch (e) {
  localStorage = {};
}

function debounce(func, wait, immediate) {
  var timeout;

  return function() {
    var context = this;
    var args = arguments;
    var later = function() {
      timeout = null;
      if (!immediate)
        func.apply(context, args);
    };
    var callNow = immediate && !timeout;

    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    if (callNow)
      func.apply(context, args);
  };
}

// sets search information default
var save_sidebar_latest = function() {
  localStorage['order_by'] = $('#sort_option').val();

  for (var i = 0; i < sidebar_keys.length; i++) {
    var key = sidebar_keys[i];

    localStorage[key] = '';

    $('input[name="' + key + '"]:checked').each(function() {
      localStorage[key] += $(this).val() + ',';
    });

    // Removing the start and last comma to avoid empty element when splitting with comma
    localStorage[key] = localStorage[key].replace(/^,|,\s*$/g, '');
  }
};

// saves search information default
var set_sidebar_defaults = function() {
  // Special handling to support adding keywords from url query param
  var q = getParam('q');
  var keywords;

  if (q) {
    keywords = decodeURIComponent(q).replace(/^,|\s|,\s*$/g, '');

    if (localStorage['keywords']) {
      keywords.split(',').forEach(function(v, k) {
        if (localStorage['keywords'].indexOf(v) === -1) {
          localStorage['keywords'] += ',' + v;
        }
      });
    } else {
      localStorage['keywords'] = keywords;
    }

    window.history.replaceState(history.state, 'Issue Explorer | Gitcoin', '/explorer');
  }

  if (localStorage['order_by']) {
    $('#sort_option').val(localStorage['order_by']);
    $('#sort_option').selectmenu().selectmenu('refresh');
  }

  for (var i = 0; i < sidebar_keys.length; i++) {
    var key = sidebar_keys[i];

    if (localStorage[key]) {
      localStorage[key].split(',').forEach(function(v, k) {
        $('input[name="' + key + '"][value="' + v + '"]').prop('checked', true);
      });

      if ($('input[name="' + key + '"][value!=any]:checked').length > 0)
        $('input[name="' + key + '"][value=any]').prop('checked', false);
    }
  }
};

var set_filter_header = function() {
  var idxStatusEl = $('input[name=idx_status]:checked');
  var filter_status = idxStatusEl.attr('val-ui') ? idxStatusEl.attr('val-ui') : 'All';

  $('#filter').html(filter_status);
};

var toggleAny = function(event) {
  if (!event)
    return;
  var key = event.target.name;
  var anyOption = $('input[name="' + key + '"][value=any]');

  // Selects option 'any' when no filter is applied
  if ($('input[name="' + key + '"]:checked').length === 0) {
    anyOption.prop('checked', true);
    return;
  }
  if (event.target.value === 'any') {
    // Deselect other filters when 'any' is selected
    $('input[name="' + key + '"][value!=any]').prop('checked', false);
  } else {
    // Deselect option 'any' when another filter is selected
    anyOption.prop('checked', false);
  }
};

var addTechStackKeywordFilters = function(value) {
  if (localStorage['keywords']) {
    localStorage['keywords'] += ',' + value;
  } else {
    localStorage['keywords'] += value;
  }

  $('.filter-tags').append('<a class="filter-tag keywords"><span>' + value + '</span>' +
    '<i class="fas fa-times" onclick="removeFilter(\'keywords\', \'' + value + '\')"></i></a>');
};

var getFilters = function() {
  var _filters = [];

  for (var i = 0; i < sidebar_keys.length; i++) {
    var key = sidebar_keys[i];

    $.each($('input[name="' + key + '"]:checked'), function() {
      if ($(this).attr('val-ui')) {
        _filters.push('<a class="filter-tag ' + key + '"><span>' + $(this).attr('val-ui') + '</span>' +
          '<i class="fas fa-times" onclick="removeFilter(\'' + key + '\', \'' + $(this).attr('value') + '\')"></i></a>');
      }
    });
  }

  if (localStorage['keywords']) {
    localStorage['keywords'].split(',').forEach(function(v, k) {
      _filters.push('<a class="filter-tag keywords"><span>' + v + '</span>' +
        '<i class="fas fa-times" onclick="removeFilter(\'keywords\', \'' + v + '\')"></i></a>');
    });
  }

  $('.filter-tags').html(_filters);
};

var removeFilter = function(key, value) {
  if (key !== 'keywords') {
    $('input[name="' + key + '"][value="' + value + '"]').prop('checked', false);
  } else {
    localStorage['keywords'] = localStorage['keywords'].replace(value, '').replace(',,', ',');

    // Removing the start and last comma to avoid empty element when splitting with comma
    localStorage['keywords'] = localStorage['keywords'].replace(/^,|,\s*$/g, '');
  }

  refreshBounties();
};

var get_search_URI = function(status) {
  var uri = ('/api/v0.1/bounties') + (status ? '_status' : '') + '?limit=' + dashboard.limit + '&offset=' + dashboard.bounty_offset;
  var keywords = '';

  for (var i = 0; i < sidebar_keys.length; i++) {
    var key = sidebar_keys[i];
    var filters = [];

    $.each ($('input[name="' + key + '"]:checked'), function() {
      if (key === 'tech_stack' && $(this).val()) {
        keywords += $(this).val() + ',';
      } else if ($(this).val()) {
        filters.push($(this).val());
      }
    });

    var val = filters.toString();

    if ((key === 'bounty_filter') && val) {
      var values = val.split(',');

      values.forEach(function(_value) {
        var _key;

        if (_value === 'createdByMe') {
          _key = 'bounty_owner_github_username';
          _value = document.contxt.github_handle;
        } else if (_value === 'startedByMe') {
          _key = 'interested_github_username';
          _value = document.contxt.github_handle;
        } else if (_value === 'fulfilledByMe') {
          _key = 'fulfiller_github_username';
          _value = document.contxt.github_handle;
        }

        if (_value !== 'any')
          uri += _key + '=' + _value + '&';
      });

      // TODO: Check if value myself is needed for coinbase
      if (val === 'fulfilledByMe') {
        key = 'bounty_owner_address';
        val = 'myself';
      }
    }

    if (val !== 'any' &&
        key !== 'bounty_filter' &&
        key !== 'bounty_owner_address') {
      uri += key + '=' + val + '&';
    }
  }

  if (localStorage['keywords']) {
    localStorage['keywords'].split(',').forEach(function(v, pos, arr) {
      keywords += v;
      if (arr.length > pos + 1) {
        keywords += ',';
      }
    });
  }

  if (keywords) {
    uri += '&raw_data=' + keywords;
  }

  if (typeof web3 != 'undefined' && web3.eth.coinbase) {
    uri += '&coinbase=' + web3.eth.coinbase;
  } else {
    uri += '&coinbase=unknown';
  }

  var order_by = localStorage['order_by'];

  if (order_by) {
    uri += '&order_by=' + order_by;
  }
  return uri;
};

var process_stats = function(results) {
  var num = results.count;
  var worth_usdt = 0;
  var stats = results.value_in_usdt + ' USD';

  for (var t in results.token_values) {
    if (Object.prototype.hasOwnProperty.call(results.token_values, t)) {
      stats += ', ' + results.token_values[t].toFixed(2) + ' ' + t;
    }
  }

  var matchesEl = $('#matches');
  var fundingInfoEl = $('#funding-info');

  switch (num) {
    case 0:
      // $('#matches').html(gettext('No Results'));
      $('#funding-info').html('');
      break;
    case 1:
      // $('#matches').html(num + gettext(' Matching Result'));
      $('#funding-info').html("<span id='modifiers'>Funded Issue</span><span id='stats' class='font-body'>(" + stats + ')</span>');
      break;
    default:
      // $('#matches').html(num + gettext(' Matching Results'));
      $('#funding-info').html("<span id='modifiers'>Funded Issues</span><span id='stats' class='font-body'>(" + stats + ')</span>');
  }
};

var paint_bounties_in_viewport = function(start, max) {
  dashboard.is_painting_now = true;
  var num_bounties = dashboard.bounties_html.length;

  for (var i = start; i < num_bounties && i < max; i++) {
    var html = dashboard.bounties_html[i];

    dashboard.last_bounty_rendered = i;
    $('#bounties').append(html);
  }

  $('div.bounty_row.result').each(function() {
    var href = $(this).attr('href');

    if (typeof $(this).changeElementType !== 'undefined') {
      $(this).changeElementType('a'); // hack so that users can right click on the element
    }

    $(this).attr('href', href);
  });
  dashboard.is_painting_now = false;
};

var near_bottom = function(callback, buffer) {
  if (!dashboard.bounties_html)
    return;
  var scrollPos = $(document).scrollTop();
  var last_active_bounty = $('.bounty_row.result:last-child');
  var window_height = $(window).height();
  var have_painted_all_bounties = dashboard.bounties_html.length <= dashboard.last_bounty_rendered;
  var does_need_to_paint_more = !dashboard.is_painting_now && ((last_active_bounty.offset().top) < (scrollPos + buffer + window_height));

  if (typeof dashboard.bounties_html == 'undefined' || dashboard.bounties_html.length == 0 || last_active_bounty.length == 0) {
    return;
  }

  if (does_need_to_paint_more) {
    callback();
  }
};


var trigger_scroll_for_refresh_api = function() {
  near_bottom(function() {
    refreshBounties(true);
  }, 1500);
};

// $(window).scroll(trigger_scroll_for_redraw);
// $('body').bind('touchmove', trigger_scroll_for_redraw);

$(window).scroll(trigger_scroll_for_refresh_api);
$('body').bind('touchmove', trigger_scroll_for_refresh_api);

var bountyToHTMLrow = function(result) {
  var related_token_details = tokenAddressToDetails(result['token_address']);
  var decimals = 18;

  if (related_token_details && related_token_details.decimals) {
    decimals = related_token_details.decimals;
  }

  var divisor = Math.pow(10, decimals);

  result['rounded_amount'] = Math.round(result['value_in_token'] / divisor * 100) / 100;
  var is_expired = new Date(result['expires_date']) < new Date() && !result['is_open'];

  // setup args to go into template
  if (typeof web3 != 'undefined' && web3.eth.coinbase == result['bounty_owner_address']) {
    result['my_bounty'] = '<a class="btn font-smaller-2 btn-sm btn-outline-dark" role="button" href="#">mine</span></a>';
  } else if (result['fulfiller_address'] !== '0x0000000000000000000000000000000000000000') {
    result['my_bounty'] = '<a class="btn font-smaller-2 btn-sm btn-outline-dark" role="button" href="#">' + result['status'] + '</span></a>';
  }
  result.action = result['url'];
  result['title'] = result['title'] ? result['title'] : result['github_url'];
  var timeLeft = timeDifference(new Date(result['expires_date']), new Date(), true);

  result['p'] = ((result['experience_level'] ? result['experience_level'] : 'Unknown Experience Level') + ' &bull; ');

  if (result['status'] === 'done')
    result['p'] += 'Done';
  if (result['fulfillment_accepted_on']) {
    result['p'] += ' ' + timeDifference(new Date(), new Date(result['fulfillment_accepted_on']), false, 60 * 60);
  } else if (result['status'] === 'started') {
    result['p'] += 'Started';
    result['p'] += ' ' + timeDifference(new Date(), new Date(result['fulfillment_started_on']), false, 60 * 60);
  } else if (result['status'] === 'submitted') {
    result['p'] += 'Submitted';
    if (result['fulfillment_submitted_on']) {
      result['p'] += ' ' + timeDifference(new Date(), new Date(result['fulfillment_submitted_on']), false, 60 * 60);
    }
  } else if (result['status'] == 'cancelled') {
    result['p'] += 'Cancelled';
    if (result['canceled_on']) {
      result['p'] += ' ' + timeDifference(new Date(), new Date(result['canceled_on']), false, 60 * 60);
    }
  } else if (is_expired) {
    var time_ago = timeDifference(new Date(), new Date(result['expires_date']), true);

    result['p'] += ('Expired ' + time_ago + ' ago');
  } else {
    var opened_when = timeDifference(new Date(), new Date(result['web3_created']), true);


    result['p'] += ('Opened ' + opened_when + ' ago, ' + expiredExpires + ' ' + timeLeft);
  }

  result['watch'] = 'Watch';
  return result;

};

var refreshBounties = function(append) {
  // manage state
  if (append && dashboard.finished_appending || dashboard.is_loading) {
    return;
  }

  dashboard.is_loading = true;
  if (append)
    dashboard.bounty_offset += dashboard.limit;

  if (!append) {
    var keywords = $('#keywords').val();
    var title = gettext('Issue Explorer | Gitcoin');

    if (keywords) {
      title = keywords + ' | ' + title;
    }

    var currentState = history.state;

    window.history.replaceState(currentState, title, '/explorer?q=' + keywords);

    save_sidebar_latest();
    set_filter_header();
    disableAny();
    getFilters();
    if (!append) {
      $('.nonefound').css('display', 'none');
      $('.bounty_row').remove();
    }
  } // filter
  var uri = get_search_URI();
  var uri_status = get_search_URI(true);
  var params = { uri: uri };

  if (!append) {
    mixpanel.track('Refresh Bounties', params);
  }
  // order
  $('.loading').css('display', 'block');
  if (!append) {
    var matchesEl = $('#matches');
    var fundingInfoEl = $('#funding-info');

    matchesEl.html('');
    fundingInfoEl.html('');
    $.get(uri_status, function(results) {
      results = sanitizeAPIResults(results);
      process_stats(results);
    });
  }
  $.get(uri, function(results) {
    results = sanitizeAPIResults(results);
    if (results.length == 0 && !append) {
      $('.nonefound').css('display', 'block');
    }
    if (results.length < dashboard.limit && append) {
      dashboard.finished_appending = true;
    }

    dashboard.is_painting_now = false;

    if (!append) {
      dashboard.last_bounty_rendered = 0;
      dashboard.bounties_html = [];
      dashboard.bounty_offset = 0;
    }


    for (var i = 0; i < results.length; i++) {
      if (results.length === 0) {
        dashboard.bounties_html = [];
        $('.nonefound').css('display', 'block');
      }
      // setup
      var result = bountyToHTMLrow(results[i]);


      // render the template
      var tmpl = $.templates('#result');
      var html = tmpl.render(result);

      dashboard.bounties_html[i + dashboard.bounty_offset] = html;
    }

    if (!append) {
      paint_bounties_in_viewport(0, dashboard.limit);
    } else {
      paint_bounties_in_viewport(dashboard.last_bounty_rendered + 1, dashboard.last_bounty_rendered + dashboard.limit + 1);
    }


  }).fail(function() {
    _alert({ message: gettext('got an error. please try again, or contact support@gitcoin.co') }, 'error');
  }).always(function() {
    dashboard.is_loading = false;
    $('.loading').css('display', 'none');
  });
};

window.addEventListener('load', function() {
  set_sidebar_defaults();
  refreshBounties();
});

var getNextDayOfWeek = function(date, dayOfWeek) {
  var resultDate = new Date(date.getTime());

  resultDate.setDate(date.getDate() + (7 + dayOfWeek - date.getDay() - 1) % 7 + 1);
  return resultDate;
};

function getURLParams(k) {
  var p = {};

  location.search.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(s, k, v) {
    p[k] = v;
  });
  return k ? p[k] : p;
}

var resetFilters = function() {
  for (var i = 0; i < sidebar_keys.length; i++) {
    var key = sidebar_keys[i];
    var tag = ($('input[name="' + key + '"][value]'));

    for (var j = 0; j < tag.length; j++) {
      if (tag[j].value == 'any')
        $('input[name="' + key + '"][value="any"]').prop('checked', true);
      else
        $('input[name="' + key + '"][value="' + tag[j].value + '"]').prop('checked', false);
    }
  }

  if (localStorage['keywords']) {
    localStorage['keywords'].split(',').forEach(function(v, k) {
      removeFilter('keywords', v);
    });
  }
};

(function() {
  if (localStorage['referrer'] === 'onboard') {
    $('#sidebar_container').addClass('invisible');
    $('#dashboard-title').addClass('hidden');
    $('#onboard-dashboard').removeClass('hidden');
    $('#onboard-footer').removeClass('hidden');
    resetFilters();
    $('input[name=idx_status][value=open]').prop('checked', true);
    $('.search-area input[type=text]').text(getURLParams('q'));

    $('#onboard-alert').click(function(e) {

      if (!$('.no-results').hasClass('hidden'))
        $('.nonefound').css('display', 'block');

      $('.bounty_row').each(function(index) {
        $(this).removeClass('hidden');
      });

      $('#onboard-dashboard').addClass('hidden');
      $('#onboard-footer').addClass('hidden');
      $('#sidebar_container').removeClass('invisible');
      $('#dashboard-title').removeClass('hidden');
      $('#dashboard-content').removeClass('hidden');

      localStorage['referrer'] = '';
      e.preventDefault();
    });
  } else {
    $('#dashboard-content').removeClass('hidden');
    $('#onboard-dashboard').addClass('hidden');
    $('#onboard-footer').addClass('hidden');
    $('#sidebar_container').removeClass('invisible');
    $('#dashboard-title').removeClass('hidden');
  }
})();

$(document).ready(function() {

  // Sort select menu
  $('#sort_option').selectmenu({
    select: function(event, ui) {
      refreshBounties();
      event.preventDefault();
    }
  });

  // TODO: DRY
  function split(val) {
    return val.split(/,\s*/);
  }

  function extractLast(term) {
    return split(term).pop();
  }

  // Handle search input clear
  $('.close-icon')
    .on('click', function(e) {
      e.preventDefault();
      $('#keywords').val('');
      $(this).hide();
    });

  $('#keywords')
    .on('input', function() {
      if ($(this).val()) {
        $('.close-icon').show();
      } else {
        $('.close-icon').hide();
      }
    })
    // don't navigate away from the field on tab when selecting an item
    .on('keydown', function(event) {
      if (event.keyCode === $.ui.keyCode.TAB && $(this).autocomplete('instance').menu.active) {
        event.preventDefault();
      }
    })
    .autocomplete({
      minLength: 0,
      source: function(request, response) {
        // delegate back to autocomplete, but extract the last term
        response($.ui.autocomplete.filter(
          dashboard.keywords, extractLast(request.term)));
      },
      focus: function() {
        // prevent value inserted on focus
        return false;
      },
      select: function(event, ui) {
        var terms = split(this.value);

        $('.close-icon').hide();

        // remove the current input
        terms.pop();

        // add the selected item
        terms.push(ui.item.value);

        // add placeholder to get the comma-and-space at the end
        terms.push('');

        this.value = '';

        addTechStackKeywordFilters(ui.item.value);

        return false;
      }
    });

  // sidebar clear
  $('.dashboard #clear').click(function(e) {
    e.preventDefault();
    resetFilters();
    refreshBounties();
  });

  // search bar
  $('#bounties').delegate('#new_search', 'click', function(e) {
    refreshBounties();
    e.preventDefault();
  });

  $('.search-area input[type=text]').keypress(function(e) {
    if (e.which == 13) {
      refreshBounties();
      e.preventDefault();
    }
  });

  // sidebar filters
  $('.sidebar_search input[type=radio], .sidebar_search label').change(function(e) {
    refreshBounties();
    e.preventDefault();
  });

  // sidebar filters
  $('.sidebar_search input[type=checkbox], .sidebar_search label').change(function(e) {
    refreshBounties(e);
    e.preventDefault();
  });

  // email subscribe functionality
  $('.save_search').click(function(e) {
    e.preventDefault();
    $('#save').remove();
    var url = '/sync/search_save';

    setTimeout(function() {
      $.get(url, function(newHTML) {
        $(newHTML).appendTo('body').modal();
        $('#save').append("<input type='hidden' name='raw_data' value='" + get_search_URI() + "'>");
        $('#save_email').focus();
      });
    }, 300);
  });

  var emailSubscribe = function() {
    var email = $('#save input[type=email]').val();
    var raw_data = $('#save input[type=hidden]').val();
    var is_validated = validateEmail(email);

    if (!is_validated) {
      _alert({ message: gettext('Please enter a valid email address.') }, 'warning');
    } else {
      var url = '/sync/search_save';

      $.post(url, {
        email: email,
        raw_data: raw_data
      }, function(response) {
        var status = response['status'];

        if (status == 200) {
          _alert({ message: gettext("You're in! Keep an eye on your inbox for the next funding listing.") }, 'success');
          $.modal.close();
        } else {
          _alert({ message: response['msg'] }, 'error');
        }
      });
    }
  };

  $('body').delegate('#save input[type=email]', 'keypress', function(e) {
    if (e.which == 13) {
      emailSubscribe();
      e.preventDefault();
    }
  });
  $('body').delegate('#save a', 'click', function(e) {
    emailSubscribe();
    e.preventDefault();
  });
});
