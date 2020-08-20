$(window).on('load',function(){
    $('#inProgressModal').modal('show');
    $('#noCategoModal').modal('show');
    // $('#postActionsModal').modal('show');
    // alert(window.location.origin); //http://localhost:9000
});

$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip(); 
}); 

$("#settings_notifications, #settings_widgets, #settings_delete_acc").click(function(){
    $("#toastMessage").toast('show'); 
});


// $('#post_list_empty').removeAttr('style')


var success_title = 'Cambios guardados con éxito', success_text = 'Los cambios fueron guardados. ', success_reloading = ' Recargando...';

function success(title, text, param){
    if($("#toastForm").hasClass("border-danger")){$("#toastForm").removeClass('border-danger'); $("#toastForm").addClass('border-success'); }
    if($("#msg_header").hasClass("bg-danger")){$("#msg_header").removeClass('bg-danger'); $("#msg_header").addClass('bg-success'); }
    $("#toastForm").addClass('border-success'); 
    $("#msg_header").addClass('bg-success'); 
    $("#msg_icon").attr('class', 'fas fa-check mr-1'); 
    $("#msg_title").text(title); 
    $("#msg_txt").text(text); 
    $("#toastForm").toast('show');

    // 0: updates personal info in settings, reloads the page
    // 1: deletes a post inside the post detail, then redirect to dashboard
    // 2: deletes a post inside the dashboard/all posts page, keeps in url but removes the element
    // 3: archives a post and ... (?)
    switch (param) {
        case 0: window.setTimeout( function() { $('#postActionsModal').modal('hide'); window.location.reload(true); }, 750);  break;
        case 1: 
            if (sender === 'detail'){
                window.setTimeout( function() { window.location.href = '/user/dashboard'; }, 750); 
            }
            else {
                $('#postActionsModal').modal('hide');
                $(`#${postID}`).delay(500).fadeOut(1000, function(){$(this).remove();}); //removing the whole table row element
            }
            break;
      
        default:  break;
      }
    
    
}


function error(title, text){
    $("#toastForm").addClass('border-danger'); 
    $("#msg_header").addClass('bg-danger'); 
    $("#msg_icon").attr('class', 'fas fa-exclamation-circle mr-1');
    $("#msg_title").text(title); 
    $("#msg_txt").text(text); 
    $("#toastForm").toast('show');
}



var sthInput = false;

function img_profile_filename(elemID){
    if (elemID === 'profile_image'){
        var path = document.getElementById('profile_image').value;//take path
        var tokens = path.split('\\');//split path
        var filename = tokens[tokens.length-1]
        var output = filename.substr(0, filename.lastIndexOf('.')) || filename;
        return(output);
    }
    else{ if(sthInput == true) { var output = elemID.substr(0, elemID.lastIndexOf('.')) || elemID; 
        // alert('el default es: ' +output) 
        } else{ return false;}
    }   
}


//Profile form
$(window).on('load',function(){

    //Default values (marked with the prefix 'd'.) They're displayed directly from db
    var d_fname = $('#profile_firstName').val(), 
        d_lname = $('#profile_lastName').val(), 
        d_title = $('#profile_title').val(), 
        d_bio = $('#profile_bio').val(), 
        d_img = img_profile_filename($('#profile_author_img').text()), 
        d_pemail = $('#profile_email').val(), 
        d_fb = $('#profile_facebook').val(), 
        d_tw = $('#profile_twitter').val(),
        d_li = $('#proprofile_linkedin').val();     

     //If user leaves the section, get default values again and fill inputs...
     $("#settings_profile").click(function(){
        $("#profile_firstName").val(d_fname); 
        $("#profile_lastName").val(d_lname); 
        $("#profile_title").val(d_title); 
        $("#profile_bio").val(d_bio); 
        $("#profile_email").val(d_pemail); 
        $("#profile_facebook").val(d_fb); 
        $("#profile_twitter").val(d_tw); 
        $("#proprofile_linkedin").val(d_li); 
    });


    $("#profile_image").change(function () {
        var validExtensions = ["jpg","jpeg","png"]
        var file = $(this).val().split('.').pop().toLowerCase();

        if (validExtensions.indexOf(file) == -1) { 
            error('Formato incorrecto', 'Solo se aceptan formatos de imagen.\nRecomendamos usar '+ validExtensions.join(', ')+'.');
            $(this).filestyle('clear'); sthInput = false; 
        } else{  if (this.files[0].size > 2097152) {
            size = (this.files[0].size/Math.pow(1024,2)).toFixed(2).slice('0, -1');
            error('Imagen demasiado grande', `La imagen seleccionada tiene un tamaño aproximado de ${size} MB, y excede el límite de tamaño permitido (2 MB).`);
            $(this).filestyle('clear'); sthInput = false; } else{ sthInput = true; }        
        }
    });

    
    $(document).on('submit', '#profile_frm',function(e){
        var data = new FormData($('#profile_frm').get(0));
        data.append('action', 'profile_Form');
        e.preventDefault();
        //New values introduced by user. If they're different than the default, then they've been changed, then update to db
        var n_fname = $('#profile_firstName').val();
        var n_lname = $('#profile_lastName').val();
        var n_title = $('#profile_title').val();
        var n_bio = $('#profile_bio').val();
        var n_img = img_profile_filename('profile_image');
        var n_pemail = $('#profile_email').val();
        var n_fb = $('#profile_facebook').val();
        var n_tw = $('#profile_twitter').val();
        var n_li = $('#proprofile_linkedin').val();

        if ((n_fname != d_fname)||(n_lname != d_lname)||(sthInput != false)||((n_img!="")&&(n_img!=d_img))||(n_title != d_title)||(n_bio != d_bio)||(n_pemail != d_pemail)||(n_fb != d_fb)||(n_tw != d_tw)||(n_li != d_li)){
            $.ajax({
                type: 'POST',
                dataType: 'json',
                url: window.location.pathname,
                data: data,
                contentType: false,
                processData: false,
                success:function(json){
                    if(json.success){success(success_title, success_text+=success_reloading, 0);}
                    else { 
                        if (json.errors == ''){error('Error en email', 'Ocurrió un error al intentar asignar el email')}
                        else{ for(var key in json.errors){error('Error en '+key, json.errors[key][0])}}
                    }
                },
            });
        }
        else {  error('Error en los datos', 'No se detectaron cambios'); }
    });
});






//Account form 

$(window).on('load',function(){

    //Default values (marked with the prefix 'd'.) They're displayed directly from db
    var d_usr = $('#acc_username').val(); 
    var d_email = $('#acc_email').val();
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
                    if(json.success){success(success_title, success_text+=success_reloading, 0);}
                    else { 
                        if (json.errors == 'email_already_taken'){error('Error en email', 'Ocurrió un error al intentar asignar el email')}
                        else{ for(var key in json.errors){error('Error en '+key, json.errors[key][0])}}
                    }
                },
            });
        }
        else { error('Error en los datos', 'No se detectaron cambios');}
    });
});




$(document).on('submit', '#newCatego_frm',function(e){
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



$('#deleteBtn_in_post_edit, #deleteBtn_in_post_list, #deleteBtn_in_dshbrd').on('click', function(){ 
    postID = $(this).data('postid');
    posttitle = $(this).data('posttitle');
    iconName = 'delete'; 
    if ($(this).attr('id') === 'deleteBtn_in_post_edit'){ post_action_config(1,1); }
    else{ post_action_config(1,2); }
});


$('#archiveBtn_in_post_edit, #archiveBtn_in_post_list').on('click', function(){ 
    postID = $(this).data('postid');
    posttitle = $(this).data('posttitle');
    iconName = 'archive'; 
    if ($(this).attr('id') === 'archiveBtn_in_post_edit'){ post_action_config(2,1); }
    else{ post_action_config(2,2); }
});

$('#unarchiveBtn_in_post_edit, #unarchiveBtn_in_post_list').on('click', function(){ 
    postID = $(this).data('postid');
    posttitle = $(this).data('posttitle');
    iconName = 'unarchive';
    if ($(this).attr('id') === 'unarchiveBtn_in_post_edit'){ post_action_config(3,1); }
    else{ post_action_config(3,2); }
});

$('#rejectBtn_in_moderate').on('click', function(){ 
    postID = $(this).data('postid');
    posttitle = $(this).data('posttitle');
    iconName = 'close';
    post_action_config(4,2)
});

$('#approveBtn_in_moderate').on('click', function(){ 
    postID = $(this).data('postid');
    posttitle = $(this).data('posttitle');
    iconName = 'check';
    post_action_config(5,2)
});

var post_action, iconName, url, where_from, postID, posttitle, sender;

function post_action_config(val, where_f){
    frm = $('#post_action_frm');
    icon = `<i class="material-icons align-top">${iconName}</i>`;
    button = $('#modal_post_action_confirm')
    label = $('#post_action_label');   
     

    switch (where_f) { case 1: sender = 'detail'; break; case 2: sender = 'dashboard'; break; default: sender = null; break; }

    switch (val) { // 1: delete, 2: archive, 3: unarchive, 4: reject
        case 1: 
            post_action = 'delete'; 
            frm.attr('method', 'DELETE');
            label.html(`¿Realmente deseas eliminar el post <b>${posttitle}</b>? (ID: ${postID})<br><br>Esta acción no se puede deshacer.`)
            button.attr('class', 'btn btn-danger px-3'); button.html(`${icon} Si, eliminar`);
        break;

        case 2: 
            post_action = 'archive'; 
            frm.attr('method', 'POST');
            label.html(`¿Realmente deseas archivar el post <b>${posttitle}</b>? (ID: ${postID})`)
            button.attr('class', 'btn btn-warning-light px-3'); button.html(`${icon} Si, archivar`);
        break;

        case 3: 
            post_action = 'unarchive'; 
            frm.attr('method', 'POST');
            label.html(`¿Sacar del archivo el post <b>${posttitle}</b>? (ID: ${postID})`)
            button.attr('class', 'btn btn-warning-light px-3'); button.html(`${icon} Si, desarchivar`);
        break;

        case 4: 
            post_action = 'reject'; 
            frm.attr('method', 'POST');
            label.html(`¿Rechazar el post <b>${posttitle}</b>? (ID: ${postID})`)
            button.attr('class', 'btn btn-danger px-3'); button.html(`${icon} Si, rechazar`);
        break;

        case 5: 
            post_action = 'approve'; 
            frm.attr('method', 'POST');
            label.html(`¿Aprobar el post <b>${posttitle}</b>? (ID: ${postID})`)
            button.attr('class', 'btn btn-success px-3'); button.html(`${icon} Si, aprobar`);
        break;
      
        default: break;
      }
}


$(document).on('submit', '#postActionsModal',function(e){
    var param; // Param is sent to success function. 0 reloads the page, 1 deletes the row 
    switch (post_action) {
        case 'delete': 
            param = 1; success_text = 'El post fue eliminado.';
            if (sender === 'detail') { success_text += ' Redireccionando...'; }
        break;

        case 'archive': 
            param = 0;  success_text = 'El post fue archivado.';
            if (sender === 'detail') { success_text += success_reloading }
        break;

        case 'unarchive': 
            param = 0; success_text = 'El post fue desarchivado.';
            if (sender === 'detail') { success_text += success_reloading }
        break;

        case 'reject': param = 1; success_text = 'El post fue rechazado.'; break;

        case 'approve': param = 1; success_text = 'El post fue aprobado.'; break;

        default: break;        
    }

    e.preventDefault();
    // alert(`post/perform-action/${post_action}/${postID}`);    
    $.ajax({
        url: `/user/post/perform-action/${post_action}/${postID}`,
        type: $(this).attr('method'),
        dataType: 'json',
        beforeSend: function (xhr) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        },
        success:function(json){
          if(json.success){success(success_title, success_text, param);}
        },
        error : function(xhr,errmsg,err) {
          console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
        });

});








function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });


