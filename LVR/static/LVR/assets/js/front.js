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



function restart_ctct_btns(isSent){
  $('#contact_frm_sending').css({'display': 'none'}).fadeOut(800);
  $('#ctct_form_send').blur();
  $('#ctct_form_send').css({'display': 'block'}).fadeIn(800);
  if(isSent == true){ $('#ctct_form_success').fadeIn(1000).css({'display': 'block'}).delay(2500).fadeOut(1000); }
  else { $('#ctct_form_error').fadeIn(1000).css({'display': 'block'}).delay(2500).fadeOut(1000); }  
}


$(document).on('submit', '#contact_frm',function(e){
  $('#ctct_form_send').css({'display': 'none'}).fadeOut(800);
  $('#contact_frm_sending').css({'display': 'block'}).fadeIn(800);
  e.preventDefault();
  $.ajax({
    type:'POST',
    url:'contact',
    dataType: 'json',
    data:{
      name:$('#contact_fullName').val(),
      email:$('#contact_email').val(),
      subject:$('#contact_subject').val(),
      msg:$('#contact_message').val(),
      csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
      action: 'sendCtct_Form',
      grecaptcha_response:grecaptcha.getResponse()
    },
    success:function(json){
      if(json.success){
        document.getElementById("contact_frm").reset();
        restart_ctct_btns(true);
        console.log('# --- JS: Captcha OK --- #')
        grecaptcha.reset();
      }
      else if(json.err_code === 'invalid_captcha'){
        $('#ctct_form_errorCaptcha').fadeIn(1000).css({'display': 'block'}).delay(2500).fadeOut(1000);
        restart_ctct_btns(false);
        console.log('# --- JS: failed captcha --- #')
      }
    },
    error : function(xhr,errmsg,err) {
      restart_ctct_btns(false);
      console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
    }
    
    });
});




$('#new_comment').submit(function(e){
  e.preventDefault();
  console.log('JS: llego aki')
  $.ajax({
    type: 'POST',
    dataType: 'json',
    data:{
      author: $('#comment_fullName').val(),
      author_email: $('#comment_email').val(),
      comment_body: $('#comment_body').val(),
      csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
      action: 'newCmt_Form',
      grecaptcha_response:grecaptcha.getResponse()
    },
    success:function(json){
      if(json.success){
        document.getElementById("new_comment").reset();
        $('html, body').animate({scrollTop: $("#new_cmt_btn").offset().top - (160)}, 1500);
        $('#newCmt').collapse('toggle');
        $('#new_cmt_success').fadeIn(1000).css({'display': 'block'}).delay(2500).fadeOut(1000);
        console.log('# --- JS: Comment Captcha OK --- #')
        grecaptcha.reset();
      }
      else if(json.err_code === 'invalid_captcha'){
        $('#new_cmt_errorCaptcha').fadeIn(1000).css({'display': 'block'}).delay(2500).fadeOut(1000);
        console.log('# --- JS: Comment failed captcha --- #')
      }
    },
    error : function(xhr,errmsg,err) {
      console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
    }
    
    });
});