$(window).on('load',function(){
    $('#inProgressModal').modal('show');
    $('#noCategoModal').modal('show');
});


$("#settings_notifications, #settings_widgets, #settings_delete_acc").click(function(){
    $("#toastMessage").toast('show'); 
});




//Account form 
$(window).on('load',function(){

    //Default values (marked with the prefix 'd'.) They're displayed directly from db
    var d_usr = $('#acc_username').val(); 
    var d_email = $('#acc_email').val();
    

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

    //If user leaves the section, get default values again and fill inputs...
    $("#settings_account").click(function(){
        $("#acc_username").val(d_usr); 
        $("#acc_email").val(d_email); 
    });
    
    $(document).on('submit', '#account_frm',function(e){
        e.preventDefault();
        //New values introduced by user. If they're different than the default, then they've been changed, then update to db
        var n_user = $('#acc_username').val();
        var n_email = $('#acc_email').val();
        if ((n_user != d_usr)||(n_email != d_email)){ 
            hasChanged = true;
            $.ajax({
                type: 'POST',
                dataType: 'json',
                url: window.location.pathname,
                data:{
                    username: $('#acc_username').val(),
                    email: $('#acc_email').val(),
                    csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
                    action: 'account_Form',
                },
                success:function(json){
                    if(json.success){success();}
                    else { 
                        if (json.errors == 'email_already_taken'){error('Error en email', 'Ocurrió un error al intentar cambiar tu email')}
                        else{ for(var key in json.errors){error('Error en '+key, json.errors[key][0])}}
                    }
                },
            });
        }
        else { error('Error en los datos', 'No se detectaron cambios en el nombre de usuario o en el email');}
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


