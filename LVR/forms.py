from django import forms as f
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from . models import blog_post, blog_author, blog_postComment, blog_category
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget
from django_summernote.fields import SummernoteTextFormField, SummernoteTextField

class PostForm(f.ModelForm):
    class Meta:
        model = blog_post
        title_attrs = {'class':'form-control form-control-lg', 'id':'post_title', 'type': 'text', 'name':'title', 'placeholder': 'Escribe el título del post'}
        subtitle_attrs = {'class':'form-control form-control-lg', 'id':'post_subtitle', 'type': 'text', 'name':'subtitle', 'placeholder': 'Escribe el subtítulo del post'}
        category_attrs = {'class':'selectpicker', 'id':'post_category', 'name':'category', 'data-style':'bs-select-form-control', 'data-title':'Selecciona una categoría', 'data-width':'100%' }
        fields = ('title', 'subtitle', 'image', 'post_body', 'category', 'tags')
        labels = {
            'title': 'Título del post',
            'subtitle': 'Subtítulo del post',
            'image': 'Imagen',
            'category': 'Categoría',
            'tags': 'Tags',
            'post_body': 'Cuerpoaaaa'
        }

        widgets = {
            'title': f.TextInput(attrs=title_attrs),
            'subtitle': f.TextInput(attrs=subtitle_attrs),
            'category': f.Select(attrs=category_attrs),
            'post_body': SummernoteWidget(),
        }


  


#Form for a new comment
class CommentForm(f.ModelForm):
    class Meta:
        model = blog_postComment
        author_attrs = {'class':'form-control form-control-lg', 'id':'comment_fullName', 'type':'text', 'name':'full-name', 'placeholder': 'Escribe tu nombre'}
        author_email_attrs = {'class':'form-control form-control-lg', 'id': 'comment_email', 'type': 'email', 'name':'author-email', 'placeholder':'Escribe tu dirección de email'}
        comment_body_attrs = {'class': 'mt-2 mt-sm-0 mt-md-0 mt-lg-0 form-control form-control-lg txtarea-maxh-400', 'id':'comment_body', 'name':'comment-body', 'rows':'5','placeholder':'Escribe tu comentario'}
        fields = ('author', 'author_email', 'comment_body')
        labels = {
            'author': 'Nombre',
            'author_email': 'Email',
            'comment_body': 'Tu comentario'
        }
        widgets = {
            'author': f.TextInput(attrs=author_attrs),
            'author_email': f.EmailInput(attrs=author_email_attrs),
            'comment_body': f.Textarea(attrs=comment_body_attrs)
        }





# Overriding the 'UserCreationForm' to allow the new following fields as inputs: email, first_name last_name
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')





class SearchForm(f.Form):
    all_posts = str(blog_post.objects.filter(status=1).count()) #counting all-time posts
    q_attrs = {'id':'search_input', 'type': 'text', 'class':'form-control border-0 mr-2', 'placeholder': 'Busca entre +'+all_posts+' posts'}
    q = f.CharField(label='Escribe una o más palabras clave', max_length=128, widget=f.TextInput(attrs=q_attrs))



class ContactForm(f.Form):
    name_attrs = {'class':'form-control form-control-lg',  'id':'contact_fullName', 'type':'text', 'name': 'fullname', 'placeholder':'Escribe tu nombre'}
    email_attrs = {'class':'form-control form-control-lg', 'id':'contact_email', 'type':'email', 'name':'email', 'placeholder':'Escribe tu email'}
    subject_attrs = {'class':'form-control form-control-lg', 'id':'contact_subject', 'type':'text', 'name':'subject', 'placeholder':'Escibe un asunto'}
    msg_attrs = {'class':'form-control form-control-lg txtarea-maxh-400', 'id':'contact_message', 'name':'message', 'rows':'2', 'placeholder':'Escribe tu mensaje (máx. 1000 caracteres)'}

    name = f.CharField(label='Nombre y apellido', max_length=128, widget=f.TextInput(attrs=name_attrs), required=True)
    email = f.EmailField(label='Correo electrónico', max_length=128, widget=f.EmailInput(attrs=email_attrs), required=True)
    subject = f.CharField(label='Asunto', max_length=128, widget=f.TextInput(attrs=subject_attrs), required=True)
    msg = f.CharField(label='Mensaje', max_length=1024, widget=f.Textarea(attrs=msg_attrs), required=True)

    
    




 









class RegistrarUsuario(f.Form):
    nombre = f.CharField(label='Nombre:',max_length=15,widget=f.TextInput())    
    telefono = f.CharField(label='Teléfono',max_length=12,widget=f.TextInput())    
    fecha_de_nacimiento = f.DateField(label='Fecha de nacimiento:', widget=f.SelectDateWidget(years=range(1900,2001)))    
    email = f.EmailField(label='Email:',max_length=254,widget=f.EmailInput())

   