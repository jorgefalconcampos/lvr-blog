from django.db import models as m
# Importing pre_save to auto-generate the post slug and post_save to auto generate/update the blog_author model
from django.db.models.signals import pre_save, post_save 
from django.dispatch import receiver
from taggit.managers import TaggableManager
from django.utils import timezone
from LeVeloRouge.utils import unique_slug_generator #Importing the auto slug generator
from django.contrib.auth.models import User
from django.db.models import Count
from django.utils.translation import gettext as _



# Author model, represents an author who writes blog posts and have access to dashboard
class blog_author(m.Model):
    name = m.OneToOneField(User, on_delete=m.CASCADE)
    slug = m.SlugField(unique=True, null=True, blank=True)
    title = m.CharField(max_length=100, blank=True)
    email = m.EmailField(unique=True, null=True)
    image = m.ImageField(upload_to='author/img/', default='author/default-img.png')
    bio = m.TextField(max_length=500)
    facebook_URL = m.URLField(null=True, blank=True)
    twitter_URL = m.URLField(null=True, blank=True)
    linkedin_URL = m.URLField(null=True, blank=True)
    activated_account = m.BooleanField(default=False)

    def __str__(self):
        return self.name.username

    @receiver(post_save, sender=User)
    def create_profile(sender, instance, created, **kwargs):
        if created:
            blog_author.objects.create(name=instance)
        instance.blog_author.save()





class blog_category(m.Model):
    name = m.CharField(max_length=100)
    description = m.CharField(max_length=300)
    slug = m.SlugField(unique=True)
    image = m.ImageField(upload_to='categories/', default='no-category.png')

    def __str__(self):
        return self.name
   




post_status = (
    (0, 'Draft'),
    (1, 'Approved'),
    (2, 'Rejected'),
    (3, 'Archived')
)

class blog_post(m.Model):
    author = m.ForeignKey(blog_author, on_delete=m.CASCADE, related_name='author')
    title = m.CharField(max_length=150)
    subtitle = m.CharField(max_length=200, blank=True) #Subtitles are optional
    slug = m.SlugField(unique=True)
    category = m.ForeignKey(blog_category, on_delete=m.CASCADE, related_name='catego', default='1')
    image = m.ImageField(upload_to='img/', default='no-img.png')
    post_body = m.TextField() #Post body
    tags = TaggableManager() #Tags
    created_date = m.DateTimeField(default=timezone.now)
    published_date = m.DateTimeField(blank=True, null=True)
    status = m.IntegerField(choices=post_status, default=0)
    # Reactions and votes for a blog post, in the same order: thumbs, fav, util, thumbs down 
    # vote_tmbup = m.IntegerField() 
    # vote_fav = m.IntegerField() 
    # vote_util = m.IntegerField() 
    # vote_tmbdn = m.IntegerField() 

    def publish(self):
        self.published_date = timezone.now()
        self.save()
    
    def approve_post(self):
        self.status = 1
        self.save()
    
    def reject_post(self):
        self.status = 2
        self.save()

    def archive_post(self):
        self.status = 3
        self.save()

    def all_cmts(self):
        return blog_postComment.objects.filter(in_post=self).count() or False

    def approved_cmts(self):
        return blog_postComment.objects.filter(in_post=self, is_approved=True).count()

    def non_approved_cmts(self):
        return blog_postComment.objects.filter(in_post=self, is_approved=False).count()
    
    def __str__(self):
        return self.title





# postComment model, represents a comment created by any reader inside a blog post
class blog_postComment(m.Model):
    in_post = m.ForeignKey(blog_post, on_delete=m.CASCADE, related_name="comments")
    author = m.CharField(max_length=125)
    author_email = m.EmailField()
    comment_body = m.TextField()
    created_date = m.DateTimeField(auto_now_add=True)
    is_approved = m.BooleanField(default=False)
    has_report = m.BooleanField(default=False)

    # approve method, to approve or disapprove comments
    def approve(self):
        self.is_approved = True
        self.save()

    def report(self):
        self.has_report = True
        self.save()

    def approved_comments(self):
        return self.blog_postComment.objects.filter(is_approved=True)

    def __str__(self):
        return 'Comment {} by {}'.format(self.comment_body, self.author)





#blog_misc model, generalized for its use inside a Privacy Policy page, Cookies page, Rules pages, etc
class blog_misc(m.Model):
    name = m.CharField(max_length=100)
    date = m.DateTimeField(default=timezone.now)
    head_desc = m.CharField(max_length=200) #Description for HTML
    bgImage = m.URLField(max_length=500)
    content = m.TextField() #Post body
    
    def __str__(self):
        return self.name





class blog_subscriber(m.Model):
    email = m.EmailField(unique=True)
    conf_num = m.CharField(max_length=15)
    confirmed = m.BooleanField(default=False)

    def __str__(self):
        return self.email + " (" + ("not " if not self.confirmed else "") + "confirmed)"





    
# Automatic slug generator for a blog post when is saved from a HTTP request (that means, a form)
def slug_generator(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(slug_generator, sender=blog_post)