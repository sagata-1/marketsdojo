var calcHeight = function() {
    var headerDimensions = $('.preview__header').height();
    $('.full-screen-preview__frame').height($(window).height() - headerDimensions);
  }

  $(document).ready(function() {
    calcHeight();
  });

  $(window).resize(function() {
    calcHeight();
  }).load(function() {
    calcHeight();
  });
