// Script to hide Special offers ticker when you click on close icon
$('.new-offers .fa-times-circle').click(function() {
  event.preventDefault();
   $('.new-offers').hide();
});

// Script which keeps the menu bar on the top when the site scrolls down.
$(function(){ 
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