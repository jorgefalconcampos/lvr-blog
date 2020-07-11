from . models import blog_post
from . forms import SearchForm, ContactForm, CommentForm


def searchPosts(request):
    form = SearchForm()
    return {'searchForm': form}


def contactMsg(request):
    form = ContactForm()
    return {'contactForm': form}


def newComment(request):
    form = CommentForm()
    return {'commntForm': form}


def get_total_posts(request):
    all_total_posts = blog_post.objects.filter(status=1).count() #counting all-time posts
    return { 'all_total_posts': all_total_posts }
