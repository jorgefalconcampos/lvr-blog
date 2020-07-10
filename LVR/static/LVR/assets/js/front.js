$(function() {
    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
      history.pushState({}, '', e.target.hash);
    });
  
    var hash = document.location.hash;
    var prefix = "tab_";
    if (hash) {
      $('.list-group a[href="'+hash.replace(prefix,"")+'"]').tab('show');
    }
  });


  
$(document).on('submit', '#contact_frm',function(e){
  $('#ctct_form_send').css({'display': 'none'}).fadeOut(800);
  $('#contact_frm_sending').css({'display': 'block'}).fadeIn(800);
  e.preventDefault();
  $.ajax({
    type:'POST',
    url:'contact',
    data:{
      name:$('#contact_fullName').val(),
      email:$('#contact_email').val(),
      subject:$('#contact_subject').val(),
      msg:$('#contact_message').val(),
      csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
      action: 'sendCtct_Form'
    },
    success:function(json){
      document.getElementById("contact_frm").reset();
      $('#contact_frm_sending').css({'display': 'none'}).fadeOut(800);
      $('#ctct_form_send').blur();
      $('#ctct_form_send').css({'display': 'block'}).fadeIn(800);
      $('#ctct_form_success').fadeIn(1000).css({'display': 'block'}).delay(2500).fadeOut(1000);
    },
    error : function(xhr,errmsg,err) {
      $('#ctct_form_error').fadeIn(1000).css({'display': 'block'}).delay(3000).fadeOut(1000);
      console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
    }
    });
});