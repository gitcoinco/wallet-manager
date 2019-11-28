$(document).ready(function() {
  let button = document.querySelector('#btn_post');

  if (button) {
    button.addEventListener(
      'click',
      function() {
        submitStatusUpdate();
      },
      false
    );
  }

  $('body').on('focus change paste keyup blur', 'textarea', function() {
    if ($(this).val().trim().length > 4) {
      $('#btn_post').attr('disabled', false);
    } else {
      $('#btn_post').attr('disabled', true);
    }
  });

  function submitStatusUpdate() {
    const data = new FormData();
    const message = $('#textarea');
    const ask = $('.activity_type_selector .active input').val();

    data.append('ask', ask);
    data.append('data', message.val().trim());
    data.append(
      'csrfmiddlewaretoken',
      $('#status input[name="csrfmiddlewaretoken"]').attr('value')
    );
    fetch('/api/v0.1/activity', {
      method: 'post',
      body: data
    })
      .then(response => {
        if (response.status === 200) {
          _alert(
            { message: gettext('Status has been saved.') },
            'success'
          );
          const activityContainer = document.querySelector('.tab-section.active .activities');

          activityContainer.setAttribute('page', 0);
          $('.tab-section.active .activities').html('');
          message.val('');
        } else {
          _alert(
            { message: gettext('An error occurred. Please try again.') },
            'error'
          );
        }
      })
      .catch(err => console.log('Error ', err));
  }
});
