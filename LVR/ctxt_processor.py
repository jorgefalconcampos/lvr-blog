from . models import blog_post

def get_total_posts(request):
    all_total_posts = blog_post.objects.filter(status=1).count() #counting all-time posts
    return { 'all_total_posts': all_total_posts }
