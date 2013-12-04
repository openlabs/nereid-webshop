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

// Script for countries and subdivisions list 

$(document).ready(function(){
  // Register on change event
  $("select#country").change(function(){
    $.getJSON("{{ url_for('nereid.website.subdivision_list') }}",
      {country: $(this).val()}, function(data){
      var options = '';
      $.each(data.result, function(index, map){
          options += '<option value="' + map.id + '" code="' + map.code + '">' + map.name + '</option>';
      });
      $("select#subdivision").html(options);
      $("select#subdivision option[value='{{ form.subdivision.data }}']").attr('selected', true);
    });
  });
  // Onload trigger the change as country comes packed with form
  $("select#country").triggerHandler("change")
  // Use client side validation on the form
  $("form#address").validate({
    errorElement: "span",
    //wrapper: "li",
    errorPlacement: function(error, element) {
      error.addClass('help-block');
      error.insertAfter(element);
    },
    highlight: function(element, errorClass) {
      $(element).parents("div.form-group").addClass("has-error");
    },
    unhighlight: function(element, errorClass) {
      $(element).parents("div.form-group").removeClass("has-error");
    },
    submitHandler: function(form) {
      $("form#address button").button('loading');
      form.submit();
    }
  });
});