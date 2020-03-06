var Cookielaw = {

  createCookie: function (name, value, days) {
    var date = new Date();
    var expires = '';

    if (days) {
      date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
      expires = '; expires=' + date.toGMTString();
    } else {
      expires = '';
    }
    document.cookie = name + '=' + value + expires + '; path=/';
  },

  createCookielawCookie: function () {
    this.createCookie('cookielaw_accepted', '1', 10 * 365);

    if (typeof (window.jQuery) === 'function') {
      if (jQuery('.sumome-react-wysiwyg-popup-container').length < 1) {
        jQuery('#CookielawBanner').slideUp();
      }
    } else {
      document.getElementById('CookielawBanner').style.display = 'none';
    }
  }

};