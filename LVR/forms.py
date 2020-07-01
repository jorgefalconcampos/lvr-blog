from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from . models import blog_post, blog_author, blog_postComment
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget
from django_summernote.fields import SummernoteTextFormField, SummernoteTextField


class PostForm(forms.ModelForm):
    class Meta:
        model = blog_post
        fields = ('title', 'subtitle', 'image', 'post_body', 'tags')
        widgets = {
            'post_body': SummernoteWidget()
        }



class CommentForm(forms.ModelForm):
    class Meta:
        model = blog_postComment
        fields = ('author', 'author_email', 'comment_body')


# Overriding the "UserCreationForm" to allow the new following fields as inputs: email, first_name last_name
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

