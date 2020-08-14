from django import forms as f
from taggit.forms import TagWidget
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from . models import blog_post, blog_author, blog_postComment, blog_category
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget
from django_summernote.fields import SummernoteTextFormField, SummernoteTextField




#Create a new post
class PostForm(f.ModelForm):
    class Meta:
        model = blog_post
        title_attrs = {'class':'form-control form-control-lg', 'id':'post_title', 'type': 'text', 'name':'title', 'placeholder': 'Escribe el título del post'}
        subtitle_attrs = {'class':'form-control form-control-lg', 'id':'post_subtitle', 'type': 'text', 'name':'subtitle', 'placeholder': 'Escribe el subtítulo del post',}
        unsplash_url_attrs = {'class':'form-control form-control-lg mr-2', 'id':'post_unsplash_url', 'type': 'URL', 'name':'unsplash_url', 'placeholder': 'https://unsplash.com/photos/urldelafoto',}
        category_attrs = {'class':'selectpicker', 'id':'post_category', 'name':'category', 'data-style':'bs-select-form-control', 'data-title':'Selecciona una categoría', 'data-width':'100%' }
        tags_attrs = {'class': 'form-control form-control-lg,', 'id': 'post_tags', 'type': 'text', 'name': 'tags', 'placeholder': 'Una lista de etiquetas separadas por coma'}
        fields = ('title', 'subtitle', 'image', 'unsplash_URL', 'post_body', 'category', 'tags')
        labels = {
            'title': 'Título del post',
            'subtitle': 'Subtítulo del post',
            'image': 'Imagen',
            'unsplash_URL': 'URL de imagen Unsplash',
            'category': 'Categoría',
            'tags': 'Tags',
            'post_body': 'Cuerpo del post'
        }

        widgets = {
            'title': f.TextInput(attrs=title_attrs),
            'subtitle': f.TextInput(attrs=subtitle_attrs),
            'unsplash_URL': f.URLInput(attrs=unsplash_url_attrs),
            'category': f.Select(attrs=category_attrs),
            'tags': TagWidget(attrs=tags_attrs),
            'post_body': SummernoteWidget(),
        }

    # name = f.CharField(label='Nombre y apellido', max_length=128, widget=f.TextInput(attrs=name_attrs), required=True)




#Create a new comment
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


#Search inside the blog
class SearchForm(f.Form):
    q_attrs = {'type': 'text', 'class':'form-control border-0 mr-2', 'placeholder': 'Busca entre todos los posts'}
    q = f.CharField(label='Escribe una o más palabras clave', max_length=128, widget=f.TextInput(attrs=q_attrs))
    def __init__(self, *args, **kwargs):
        super (SearchForm, self).__init__(auto_id=True, *args, **kwargs)
        all_posts = str(blog_post.objects.filter(status=1).count()) #counting all-time posts
        self.fields['q'].widget.attrs['placeholder'] = 'Busca entre +'+all_posts+' posts'


#To edit the account form (in the account section)
class AccountEditUserForm(UserChangeForm):
    usernme_attrs = {'class':'form-control', 'id':'acc_username', 'type': 'text', 'name':'username', 'placeholder': 'Escribe un nombre de usuario'}
    email_attrs = {'class':'form-control', 'id':'acc_email', 'type': 'email', 'name':'email', 'placeholder': 'Escribe un email'}
        
    username = f.CharField(label='Nombre de usuario', max_length=32, widget=f.TextInput(attrs=usernme_attrs))
    email = f.EmailField(label='Email privado', max_length=64, widget=f.EmailInput(attrs=email_attrs))
        
    class Meta:
        model = User
        fields = ('username', 'email')


     

# The 'ProfileEditUserForm' and 'ProfileEditAuthorForm' classes are for the same form (profile setting in dashboard)
class ProfileEditUserForm(f.ModelForm):
    first_name_attrs = {'class':'form-control', 'id':'profile_firstName', 'type': 'text', 'placeholder': 'Escribe tu nombre'}
    last_name_attrs = {'class':'form-control', 'id':'profile_lastName', 'type': 'text', 'placeholder': 'Escribe tu apellido'}

    first_name = f.CharField(label='Nombre', max_length=32, widget=f.TextInput(attrs=first_name_attrs))
    last_name = f.CharField(label='Apellido', max_length=32, widget=f.TextInput(attrs=last_name_attrs))
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


# The 'ProfileEditUserForm' and 'ProfileEditAuthorForm' classes are for the same form (profile setting in dashboard)
class ProfileEditAuthorForm(f.ModelForm):
    title_attrs = {'class':'form-control', 'id':'profile_title', 'type':'text', 'placeholder':'Redactor, ingeniero, padre de familia, maestro Jedi...' }
    bio_attrs = {'class':'form-control txtarea-maxh-200', 'id':'profile_bio', 'rows':'2', 'placeholder':'Cuéntale a los lectores un poco de ti y de tu vida :)'}
    email_attrs = {'class':'form-control', 'id':'profile_email', 'name':'email_url', 'type':'email', 'placeholder':'usuario@dominio.com'}
    image_attrs = { 'class':'filestyle', 'id':'profile_image', 'type':'file', 'data-buttonBefore':'true', 'data-size':'sm', 'data-text':'Subir foto',
        "data-icon":"<i class='fas fa-file-image pr-2'></i>", 'data-btnClass':'btn-dark px-3', 'data-placeholder':'Ningún archivo seleccionado' }
    fb_attrs = {'class':'form-control', 'id':'profile_facebook', 'name':'facebook_url', 'type':'url', 'placeholder':'https://www.facebook.com/myprofile' }
    tw_attrs = {'class':'form-control', 'id':'profile_twitter', 'name':'twitter_url', 'type':'url', 'placeholder':'https://www.twitter.com/myprofile' }
    li_attrs = {'class':'form-control', 'id':'profile_linkedin', 'name':'linkedin_url', 'type':'url', 'placeholder':'https://www.linkedin.com/myprofile' }

    title = f.CharField(label='Título', max_length=32, widget=f.TextInput(attrs=title_attrs))
    bio = f.CharField(label='Biografía', max_length=128, widget=f.Textarea(attrs=bio_attrs))
    email = f.EmailField(label='Email público', max_length=32, widget=f.EmailInput(attrs=email_attrs), required=False)
    image = f.ImageField(widget=f.FileInput(attrs=image_attrs), required=False, help_text='Sube una foto cuadrada de 300x300 píxeles en formato .jpg o .png. El tamaño de la foto debe ser menor a 2 MB.' )
    facebook_URL = f.URLField(max_length=256, widget=f.TextInput(attrs=fb_attrs), required=False)
    twitter_URL = f.CharField(max_length=256, widget=f.TextInput(attrs=tw_attrs), required=False)
    linkedin_URL = f.CharField(max_length=256, widget=f.TextInput(attrs=li_attrs), required=False)

    class Meta:
        model = blog_author
        fields = ('title', 'bio', 'email', 'image', 'facebook_URL', 'twitter_URL', 'linkedin_URL')


class NewCategory(f.ModelForm):
    class Meta:
        model = blog_category
        name_attrs = {'class':'form-control form-control-lg', 'id':'catego_name', 'type':'text', 'name':'name', 'placeholder': 'Escribe el nombre de la categoría'} 
        desc_attrs = {'class': 'form-control form-control-lg', 'id':'catego_desc', 'type':'text', 'name':'description', 'placeholder': 'Escribe una breve descripción de la categoría'}     

        fields = ('name', 'description', 'image')
        labels = {
            'name': 'Nombre de la categoría',
            'description': 'Descripción de la categoría',
            'image': 'Imagen'
        }

        widgets = {
            'name': f.TextInput(attrs=name_attrs),
            'description': f.TextInput(attrs=desc_attrs),
        }


#Send contact mail
class ContactForm(f.Form):
    name_attrs = {'class':'form-control form-control-lg',  'id':'contact_fullName', 'type':'text', 'name': 'fullname', 'placeholder':'Escribe tu nombre'}
    email_attrs = {'class':'form-control form-control-lg', 'id':'contact_email', 'type':'email', 'name':'email', 'placeholder':'Escribe tu email'}
    subject_attrs = {'class':'form-control form-control-lg', 'id':'contact_subject', 'type':'text', 'name':'subject', 'placeholder':'Escibe un asunto'}
    msg_attrs = {'class':'form-control form-control-lg txtarea-maxh-400', 'id':'contact_message', 'name':'message', 'rows':'2', 'placeholder':'Escribe tu mensaje (máx. 1000 caracteres)'}

    name = f.CharField(label='Nombre y apellido', max_length=128, widget=f.TextInput(attrs=name_attrs), required=True)
    email = f.EmailField(label='Correo electrónico', max_length=128, widget=f.EmailInput(attrs=email_attrs), required=True)
    subject = f.CharField(label='Asunto', max_length=128, widget=f.TextInput(attrs=subject_attrs), required=True)
    msg = f.CharField(label='Mensaje', max_length=1024, widget=f.Textarea(attrs=msg_attrs), required=True)


#Subscribe to newsletter
class SubscribeForm(f.Form):
    s_email_attrs = {'class':'form-control bg-none border-dark text-white', 'id':'sub_email', 'type':'email', 'name':'sub_email', 'placeholder':'Escribe tu dirección de email'}
    s_email = f.EmailField(label='Suscríbete al newsletter', max_length=128, widget=f.EmailInput(attrs=s_email_attrs), required=True)



   