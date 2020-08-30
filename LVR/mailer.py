import logging, random
from django.core import mail #EmailMessage lives here
from django.http import JsonResponse
from django.utils.text import format_lazy as fl
from django.conf import settings as conf_settings
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from django.core.mail.backends.smtp import EmailBackend
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail, get_connection, send_mass_mail
from . models import blog_post, blog_author, blog_postComment, blog_misc, blog_subscriber






class BaseMailer():
    def __init__(self, message_to, context, subject, template, sndr_host, sndr_username, sndr_pass, sndr_port, sndr_tls, **substitutions):

        self.con = mail.get_connection()

        self.message_to = message_to
        self.subject = subject
        self.body_msg = render_to_string(template, context)
        
        self.sndr_host = sndr_host
        self.sndr_port = sndr_port
        self.sndr_username = sndr_username
        self.sndr_pass = sndr_pass
        self.sndr_tls = sndr_tls

        # sth like request o algo asi xd
        self.substitutions = { }

        for key in substitutions:
            self.substitutions.update({key:substitutions[key]})

    def create_email(self):
        # creating connection
        self.con.open()

        #filling the connection (EmailBackend) object
        self.mail_obj = EmailBackend(
            host=self.sndr_host, 
            port=self.sndr_port, 
            username=self.sndr_username, 
            password=self.sndr_pass, 
            use_tls=self.sndr_tls)

        # filling the EmailMessage object
        self.mail = mail.EmailMessage(
            subject=self.subject, 
            body=self.body_msg, 
            from_email=self.sndr_username,
            to=[self.message_to],
            connection=self.con )
  
    def send_email(self):
        self.create_email()
        try:
            self.mail.content_subtype = 'html'
            # self.con.send_messages([self.mail])
            self.mail_obj.send_messages([self.mail])
            self.con.close()
            return True
        except Exception as e:
            print(f'\n\n# --- PY: Error sending email: --- #\n{e}')
            return False



class SendNewsletterConfirmation(BaseMailer):
    def __init__(self, message_to, context, **substitutions):
        super().__init__(
            message_to, 
            context,
            subject = _('str_confirmYourEmail'), 
            template = 'LVR/mails/blog/confirm-mail.html',
            sndr_host = conf_settings.EMAIL_HOST, 
            # ---- change only username and pass
            sndr_username = conf_settings.NEWSLETTER_HOST_USER, 
            sndr_pass = conf_settings.NEWSLETTER_HOST_PASSWORD, 
            # change only username and pass ----
            sndr_port = conf_settings.EMAIL_PORT,
            sndr_tls = conf_settings.EMAIL_USE_TLS,
            **substitutions
            )

class SendConfirmationMail(BaseMailer):
    def __init__(self, message_to, context, **substitutions):
        super().__init__(
            message_to,
            context,
            subject = fl('{} {} {}', _('str_mails_activationMail4'), substitutions["first_name"], substitutions["last_name"]),
            template = 'LVR/mails/user/activate-email.html',
            sndr_host = conf_settings.EMAIL_HOST,
            # ---- change only username and pass
            sndr_username = conf_settings.USERS_HOST_USER, 
            sndr_pass = conf_settings.USERS_HOST_PASSWORD, 
            # change only username and pass ----
            sndr_port = conf_settings.EMAIL_PORT,
            sndr_tls = conf_settings.EMAIL_USE_TLS,
            **substitutions         
        )


