import random
from django.core import mail
from . models import blog_subscriber
from django.db import IntegrityError
from django.shortcuts import reverse

from . tokens import account_activation_token
from django.core.mail import get_connection, send_mass_mail, EmailMessage
from django.conf import settings as conf_settings
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.contrib.sites.shortcuts import get_current_site
from . mailer import SendNewsletterConfirmation, SendConfirmationMail
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode



def generate_random_digits():
    return "%0.12d" % random.randint(0, 999999999999)



def mail_newsletter(message_to, subject, template, context, is_massive, request):
    try:
        con = mail.get_connection()
        con.open()
        print(f'\n\n# --- PY: Django connected to the SMTP Server --- #\n')
        host=conf_settings.NEMAIL_HOST
        host_username=conf_settings.NEMAIL_HOST_USER
        host_password=conf_settings.NEMAIL_HOST_PASSWORD
        host_port=conf_settings.NEMAIL_PORT
        host_use_tls=conf_settings.NEMAIL_USE_TLS
        print(f'\n\n# --- PY: Email details: --- #\n\n- Host: <<{host}>>\n- User: <<{host_username}>>\n- Port: <<{host_port}>>\n- Use TLS: <<{host_use_tls}>>')
        mail_obj = EmailBackend(host=host, port=host_port, username=host_username, password=host_password, use_tls=host_use_tls)
        
        if is_massive:
            cntx = {}
            mail_subject = subject            
            message_from = conf_settings.NEMAIL_HOST_USER
            domain = get_current_site(request).domain  
            try:
                for c in context:
                    cntx['email']=c[0]
                    cntx['cnumber']=c[1]
                    cntx['unsubscribe'] = '{}?id={}'.format(request.build_absolute_uri('/unsubscribe/'), c[1])
                    message = render_to_string(template, cntx)
                    msg = mail.EmailMessage(subject=mail_subject, body=message, from_email=host_username, to=[c[0]], connection=con)
                    msg.content_subtype = 'html'
                    mail_obj.send_messages([msg])

                    print(f'# --- PY: Message sent to <<{c[0]}>> --- #')

            except Exception as e:
                print(f'\n\n# --- PY: Error sending massive email: --- #\n{e}')
            
            # print(f'\n\n# --- PY: (helpers.py) Sending email to... --- #\n')
            # for (i, sub) in enumerate(message_to, start=1):
            #     print(f"> {i}: {sub['email']}, {sub['conf_num']}")
                
         

            print('A todos los del Newsletter')
            return True
        else:
            mail_subject = subject
            message = render_to_string(template, context)
            message_from = conf_settings.NEMAIL_HOST_USER
            msg = mail.EmailMessage(subject=mail_subject, body=message, from_email=host_username, to=[message_to], connection=con)
            msg.content_subtype = 'html'
            mail_obj.send_messages([msg])
            

            print(f'\n\n# --- PY: Email sent successfully to <<{message_to}>> --- #\n')
            return True
    except Exception as e:
        print(f'\n\n# --- PY: There was an error sending the email: --- #\n{e} \nend of error')
        return False


def mail_newsletterv2(subscriber_email, request):
    rnd = generate_random_digits()
    conf_url ="{}?id={}".format(request.build_absolute_uri('/confirm'), rnd)
    print(f'\n\n# --- PY: Confirmation URL: --- #\n{conf_url}')
    # if 2 users use the same email at the same time (weird scenario, but possible) then the 
    # fastest request will get the confirm email, the second will get an error 
    try:
        sub = blog_subscriber(email=subscriber_email, conf_num=rnd)
        sub.save()
    except IntegrityError as e:
        if 'UNIQUE constraint' in str(e.args):
            return False

    context = {'email': subscriber_email, 'confirmation_url': conf_url}

    if SendNewsletterConfirmation(subscriber_email, context).send_email():
        return True
    else:
        sub.delete()
        return False
  
        


def send_activation_linkv2(user, request):
    uid = urlsafe_base64_encode(force_bytes(user.id))
    token = account_activation_token.make_token(user)    
    url_args = reverse('activate', kwargs={ 'uidb64':uid, 'token':token })
    url = request.build_absolute_uri(url_args)
    # context passed to HTML template
    context = {'name': user.first_name, 'username': user.username, 'url':url, 'uid': uid, 'token': token }  
   
    if SendConfirmationMail(user.email, context, first_name=user.first_name, last_name=user.last_name).send_email():
        return True
    else:
        return False






       
                   