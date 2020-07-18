"""LeVeloRouge URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# -------------------#
#    Project URL'S   #
# -------------------#

from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include
from django.conf.urls import url, handler404
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.contrib import admin
from LVR.views import page_not_found_404
from LVR import views



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('LVR.urls')),
    path('', include('pwa.urls')),
    path('summernote/', include('django_summernote.urls')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    path('user/password-reset/', auth_views.PasswordResetView.as_view(
        template_name='LVR/user/pswd/password-reset.html', subject_template_name='LVR/mails/user/pswd/reset-pass-mail-subj.txt',
        html_email_template_name='LVR/mails/user/pswd/reset-pass-mail.html'),name='password_reset'),    
    path('user/password-reset/done', auth_views.PasswordResetDoneView.as_view(template_name='LVR/user/pswd/password-reset-done.html'), name='password_reset_done'),
    path('user/password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='LVR/user/pswd/password-reset-confirm.html'),name='password_reset_confirm'),
    path('user/password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='LVR/user/pswd/password-reset-complete.html'),name='password_reset_complete'),
]

handler404 = 'LVR.views.page_not_found_404'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path('', include('LVR.urls')), 
)

