from . import views
from django.urls import path
from django.contrib import admin


# -------------------#
#    App URL'S   #
# -------------------#


urlpatterns = [
    #base:
    path("robots.txt", views.robots_txt),
    path('', views.base, name='base'),
    path('home', views.index, name='index'),
    path('search', views.search, name='search'),
    path('cm', views.cm, name='cm'),
    path('contact', views.contact, name='contact'),
    path('getdata', views.getdata, name='getdata'),
    #subscriber
    path('subscribe', views.subscribe, name='subscribe'),
    path('confirm/', views.confirm_subscribe, name='confirm'),
    path('unsubscribe/', views.unsubscribe, name='unsubscribe'),
    #blog
    path('about', views.about, name='about'),  
    path('post/<slug:category_text>/<slug:slug_text>/', views.post_detail, name='post_detail'),
    path('tags', views.tags, name='tags'),
    path('tags/<slug:slug>', views.tags_detail, name='tags_detail'),
    path('categories', views.categories, name='categories'),
    path('categories/<slug:slug>', views.categories_detail, name='categories_detail'),
    path('authors', views.authors, name='authors'),
    path('authors/<slug:pinchiautor>/', views.author_detail, name='author_detail'),
    #misc:
    path('da-rules', views.rules, name='rules'),
    path('cookies', views.cookies, name='cookies'),
    path('service-terms', views.service_terms, name='service_terms'),
    path('comments-terms', views.comments_terms, name='comments_terms'),
    path('privacy-policy', views.privacy_policy, name='privacy_policy'),

    # user/author:
    path('user/login', views.login, name='login'),
    path('user/signup', views.sign_up, name='signup'),
    path('user/moderate', views.moderate_posts, name='moderate'),
    path('user/category/new', views.new_category, name='new_category'),
    path('user/profile', views.profile, name='profile'),    
    path('user/settings', views.settings, name='settings'),
    path('user/dashboard', views.dashboard, name='dashboard'),
    path('user/calendar', views.calendar, name='calendar'),
    path('user/notifications', views.notifications, name='notifications'),
    path('user/notifications', views.notifications, name='notifications'),
    path('user/tasks', views.tasks, name='tasks'),
    path('user/posts/', views.post_list, name='post_list'),
    path('user/post/new', views.post_new, name='post_new'),
    path('user/post/edit/<slug:slug_text>', views.post_edit, name='post_edit'),
    path('activate/<str:uidb64>/<str:token>/', views.activate, name='activate'),
    path('user/account-activated/<str:user>', views.signup_account_activated, name='account_activated'),
    # path('user/password-reset', views.password_reset, name='password_reset'),
    path('delete/<slug:slug_text>', views.post_delete, name='post_delete'),
    path('archive/<slug:slug_text>', views.post_archive, name='post_archive'),
    path('user/logout', views.logout, name='logout'),

    #others:

]
