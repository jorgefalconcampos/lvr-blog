from . models import blog_post
from . forms import SearchForm, ContactForm, CommentForm, SubscribeForm, NewCategory


#In a ideal scenario, there'll be only 3: seacrh posts, contact message and subscribe to newsletter

def searchPosts(request):
    form = SearchForm()
    return {'searchForm': form}


def contactMsg(request):
    form = ContactForm()
    return {'contactForm': form}


def newComment(request):
    form = CommentForm()
    return {'commntForm': form}


def subscribeNewsletter(request):
    form = SubscribeForm()
    return {'subscribeForm': form}


def newCategory(request):
    form = NewCategory()
    return {'newCategoryForm': form}
