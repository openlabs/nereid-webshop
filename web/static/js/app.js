$('.new-offers .fa-times-circle').click(function() {
  event.preventDefault();
   $('.new-offers').hide();
});
$(function(){ // document ready
  var stickyTop = $('.sticky').offset().top; // returns number
  $(window).scroll(function(){ // scroll event
    var windowTop = $(window).scrollTop(); // returns number
    if (stickyTop < windowTop) {
      $('.sticky').css({ position: 'fixed', top: 0 });
    } else {
      $('.sticky').css('position','static');
    }
  });
});
$(document).ready(function(){
  $('a').click(function(){
    var el = $(this).attr('href');
    var elWrapped = $(el);
    scrollToDiv(elWrapped,40);
    return false;
  });
});