$(function() {
  $('.username-search').select2({
    ajax: {
      url: '/api/v0.1/users_search/?token=' + currentProfile.githubToken,
      dataType: 'json',
      delay: 250,
      data: function(params) {

        let query = {
          term: params.term[0] === '@' ? params.term.slice(1) : params.term
        };

        return query;
      },
      processResults: function(data) {
        return {
          results: data
        };
      },
      cache: true
    },
    placeholder: 'Search by username',
    minimumInputLength: 3,
    escapeMarkup: function(markup) {

      return markup;
    },
    templateResult: formatUser,
    templateSelection: formatUserSelection
  });

  // fix for wrong position on select open
  var select2Instance = $('.username-search').data('select2');

  select2Instance.on('results:message', function(params) {
    this.dropdown._resizeDropdown();
    this.dropdown._positionDropdown();
  });

  function formatUser(user) {

    if (user.loading) {
      return user.text;
    }
    let markup = `<div class="d-flex align-items-baseline">
                    <div class="mr-2">
                      <img class="rounded-circle" src="${user.avatar_url || static_url + 'v2/images/user-placeholder.png'}" width="40" height="40"/>
                    </div>
                    <div class="">${user.text}</div>
                  </div>`;

    return markup;
  }

  function formatUserSelection(user) {

    let selected;

    if (user.id) {
      selected = `<img class="rounded-circle" src="${user.avatar_url || static_url + 'v2/images/user-placeholder.png'}" width="20" height="20"/> ${user.text}`;
    } else {
      selected = user.text;
    }
    return selected;
  }
});
