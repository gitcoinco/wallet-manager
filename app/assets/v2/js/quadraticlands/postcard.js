$(document).ready(function() {
  var base_url = '/quadraticlands/mission/postcard/svg?';
  var $target = $('#target');

  $('#text').keyup(function() {
    update_output();
  });
  $('.backgrounds li').click(function() {
    $(this).parents('.parent').find('li').removeAttr('selected');
    $(this).attr('selected', 'selected');
    update_output();
  });
  var update_output = function() {
    let text = $('#text').val();

    text = text.replace(/[\r\n]/gm, ' NEWLINE ');
    const selected = $('li[selected=selected]');
    let attrs = `&text=${text}`;

    for (let i = 0; i < selected.length; i++) {
      const key = $(selected[i]).attr('name');
      const val = $(selected[i]).attr('value');

      attrs += `&${key}=${val}`;
    }
    const url = base_url + attrs;

    $target.attr('src', url);
    var new_url = '/quadraticlands/mission/postcard';

    history.pushState({}, null, new_url + '?' + attrs);
  };

  var keys = [
    'front_background',
    'back_background',
    'front_frame',
    'color'
  ];

  for (var i = 0; i < keys.length; i++) {
    var key = keys[i];

    if (getParam(key)) {
      $('li[name=' + key + ']').removeAttr('selected');
      $('li[name=' + key + '][value=' + getParam(key) + ']').attr('selected', 'selected');
    }
  }

  var text = getParam('text');

  if (text) {
    text = text.replaceAll(' NEWLINE ', '\n');

    $('#text').val(text);
  }

  update_output();
});
