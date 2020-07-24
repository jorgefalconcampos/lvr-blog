$(window).on('load',function(){
    $('#inProgressModal').modal('show');
    $('#noCategoModal').modal('show');
});


$("#settings_notifications, #settings_widgets, #settings_delete_acc").click(function(){
    $("#toastMessage").toast('show'); 
});



$(window).on('load',function(){
    

    function success(){
        if($("#toastForm").hasClass("border-danger")){$("#toastForm").removeClass('border-danger'); $("#toastForm").addClass('border-success'); }
        if($("#msg_header").hasClass("bg-danger")){$("#msg_header").removeClass('bg-danger'); $("#msg_header").addClass('bg-success'); }
        $("#toastForm").addClass('border-success'); 
        $("#msg_header").addClass('bg-success'); 
        $("#msg_icon").attr('class', 'fas fa-check mr-1'); 
        $("#msg_title").text('Cambios guardados con éxito'); 
        $("#msg_txt").text('Los cambios fueron guardados. Recargando esta página...'); 
        $("#toastForm").toast('show');
        window.setTimeout( function() {window.location.reload(true);}, 1500);
    }

    function error(title, text){
        $("#toastForm").addClass('border-danger'); 
        $("#msg_header").addClass('bg-danger'); 
        $("#msg_icon").attr('class', 'fas fa-exclamation-circle mr-1');

        $("#msg_title").text(title); 
        $("#msg_txt").text(text); 
        $("#toastForm").toast('show');
    }

    var hasChanged = false;
    
    var d_usr = $('#acc_username').val();
    var d_email = $('#acc_email').val();
    $("#settings_account").click(function(){
        $("#acc_username").val(d_usr); 
        $("#acc_email").val(d_email); 
    });
    
    $('#account_frm').submit(function(e){
        hasChanged = true;
        e.preventDefault();
        $.ajax({
        type: 'POST',
        dataType: 'json',
        data:{
            username: $('#acc_username').val(),
            email: $('#acc_email').val(),
            csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
            action: 'account_Form',
        },
        success:function(json){
            if(json.success){success();}
            else { 
                if (json.errors == 'email_already_taken'){error('Error en email', 'El email que proporcionaste ya está en uso')}
                else{ for(var key in json.errors){error('Error en '+key, json.errors[key][0])}}
            }
        },
        });
    });
    
});





$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip(); 
}); 


$(document).on('submit', '#newCatego_frm',function(e){
    $("#txt").remove();
    var data = new FormData($('#newCatego_frm').get(0));
    e.preventDefault();
    $.ajax({
        type: 'POST',
        url: window.location.pathname,
        dataType: 'json',
        data: data,
        contentType: false,
        processData: false,
        success: function(json){
            if(json.success){     
                document.getElementById("newCatego_frm").reset();
                $('#newCatego_form_success').fadeIn(700).css({'display': 'block'}).delay(2000).fadeOut(700);
            }
            else if (json.err_code == 'already_exists'){
                $('#newCatego_form_error').append('<span id="txt">: ya existe esa categoría</span>');
                $('#newCatego_form_error').fadeIn(700).css({'display': 'block'}).delay(2000).fadeOut(700);
            }
            else { alert(json.err_code); }
        },
        error : function(xhr,errmsg,err) {
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });
    return false;
});



$(document).on('submit', '#account_frm',function(e){
    // $('#subscribe_send').css({'display': 'none'}).fadeOut(800);
    // $('#subscribe_sending').css({'display': 'inline-block'}).fadeIn(800);
    e.preventDefault();
    $.ajax({
      type: 'POST',
      url: window.location.pathname,
      dataType: 'json',
      data:{
        username: $('#acc_username').val(),
        email: $('#sub_email').val(),
        csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
        action: 'subscribe_Form',
      },
      success:function(json){
        if(json.success){
          document.getElementById("subscribe_frm").reset();
          restart_subcribe_btns(true);
          console.log('# --- JS: OK --- #')
        }
        else{
          if(json.already_exists == true){
            $('#subscribe_already_error').fadeIn(1000).css({'display': 'block'}).delay(2500).fadeOut(1000);
            $('#subscribe_sending').css({'display': 'none'}).fadeOut(800);
            $('#subscribe_send').css({'display': 'inline'}).fadeIn(800);
          } else{ restart_subcribe_btns(); }
          console.log('# --- JS: Failed try of subscription --- #')
        }
      },
      error : function(xhr,errmsg,err) {
        console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
      }  
      });
  });