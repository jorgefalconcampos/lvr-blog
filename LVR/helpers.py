import random
from django.core import mail
from django.core.mail import get_connection, send_mass_mail, EmailMessage
from django.conf import settings as conf_settings
from django.template.loader import render_to_string
from django.core.mail.backends.smtp import EmailBackend
from django.contrib.sites.shortcuts import get_current_site



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