from django import forms as f
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from . models import blog_post, blog_author, blog_postComment
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget
from django_summernote.fields import SummernoteTextFormField, SummernoteTextField


class PostForm(f.ModelForm):
    class Meta:
        model = blog_post
        fields = ('title', 'subtitle', 'image', 'post_body', 'category', 'tags')
        widgets = {
            'post_body': SummernoteWidget()
        }



#Form for a new comment
class CommentForm(f.ModelForm):
    class Meta:
        author_attrsv2 = {'class':'form-control form-control-lg', 'id':'comment_fullName', 'type':'text', 'name':'full-name', 'placeholder': 'Escribe tu nombre'}
        author_email_attrsv2 = {'class':'form-control form-control-lg', 'id': 'comment_email', 'type': 'email', 'name':'author-email', 'placeholder':'Escribe tu dirección de email'}
        comment_body_attrsv2 = {'class': 'mt-2 mt-sm-0 mt-md-0 mt-lg-0 form-control form-control-lg txtarea-maxh-400', 'id':'comment_body', 'name':'comment-body', 'rows':'5','placeholder':'Escribe tu comentario'}


        model = blog_postComment
        fields = ('author', 'author_email', 'comment_body')
        labels = {
            'author': 'Nombre',
            'author_email': 'Email',
            'comment_body': 'Tu comentario'
        }
        widgets = {
            'author': f.TextInput(attrs=author_attrsv2),
            'author_email': f.EmailInput(attrs=author_email_attrsv2),
            'comment_body': f.Textarea(attrs=comment_body_attrsv2)
        }





# Overriding the "UserCreationForm" to allow the new following fields as inputs: email, first_name last_name
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

