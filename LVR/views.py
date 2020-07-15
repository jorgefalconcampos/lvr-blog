from django.utils import timezone
import datetime, math, json, urllib, smtplib
from django.template.defaultfilters import date
from django.contrib.auth.models import User
from django.core import serializers, mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404, HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.shortcuts import redirect, render, get_object_or_404, reverse
from . models import blog_post, blog_category, blog_author, blog_postComment, blog_misc, blog_subscriber  #Importing the models
from . forms import PostForm, CommentForm, CreateUserForm, ContactForm, SubscribeForm
from django.utils.translation import gettext as _
from django.conf import settings as conf_settings #To read reCaptcha's key
from . decorators import check_recaptcha
from . helpers import generate_random_digits, mail_newsletter
from taggit.models import Tag
from django.db.models import Count, Q
from django.db.models.functions import Upper
from decouple import config
from django.views.decorators.http import require_GET

#User, Admin & Superuser
from django.utils.text import slugify
from django.contrib import messages #To customize login & signup forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate, login as do_login, logout as do_logout
from django.contrib.auth.decorators import login_required, user_passes_test # upt is to restrict to super user only
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.template.loader import render_to_string
from . tokens import account_activation_token
from django.core.mail import EmailMessage, get_connection, send_mail
from django.core.mail.backends.smtp import EmailBackend
# from LeVeloRouge.settings import NEMAIL_HOST_USER
from .tokens import account_activation_token




# ==============================#
# ====== Config section ====== #
# =============================#


@require_GET
def robots_txt(request):
    lines = [
        "User-Agent: *",
        "Disallow: /private/",
        "Disallow: /junk/",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain") 


# ============================#
# ====== Base section ====== #
# ============================#


def getdata(request):
    results = blog_post.objects.all()
    jsondata = serializers.serialize('json',results)
    return HttpResponse(jsondata)



def base(request):
    template = 'LVR/base.html' 
    if request.method == 'GET':
        return redirect('index')
    return render(request, template)

def cm(request):
    # notify_new(request)
    # return render(request, 'LVR/user/contact-mail.html', {})
    # context = {'action': 'deleted'}
    # return render(request, 'LVR/mails/blog/average-mail.html')
    return render(request, 'LVR/user/aa-wrong-link.html')


    # return render(request, 'LVR/mails/blog/verify.html')

    

#For searching a blog_post object 
def search(request):
    template = 'LVR/search.html'
    if request.method == 'GET':
        search_term = request.GET.get('q')
        bad_query = False

        if not search_term:
            return render(request, template, {'empty_search':True})

        if len(search_term) <= 2:
            bad_query = True
        else:
            queryset = []
            queries = search_term.split(" ") #python install 2019 --> [python, install, 2019]
            for q in queries:
                posts = blog_post.objects.filter(
                    Q(title__icontains=q)|
                    Q(subtitle__icontains=q)|
                    Q(post_body__icontains=q)).distinct()

            for post in posts:
                queryset.append(post)
            
            context = {'results': queryset, 'number': len(queryset), 'query': search_term}
            return render(request, template, context)

    return render(request, template, {'bad_query':bad_query} )



#This method allows blog readers get in touch with <<Le vélo rouge>>
@check_recaptcha
def contact(request):
    response_data = {}
    if request.POST.get('action') == 'sendCtct_Form':
        ctct_form = ContactForm(data=request.POST)
        if ctct_form.is_valid() and request.recaptcha_is_valid:
            print('\n\n# --- PY: Form & Captcha passed --- #')
            template = 'LVR/user/contact-mail.html'
            msg_sender = request.POST.get('name')
            msg_email = request.POST.get('email') 
            msg_subject = request.POST.get('subject')
            msg_msg = request.POST.get('msg')

            response_data['success'] = True
            response_data['name'] = msg_sender
            response_data['email'] = msg_email
            response_data['subject'] = msg_subject
            response_data['msg'] = msg_msg

            context = {'name': msg_sender, 'email': msg_email, 'subject': msg_subject, 'msg': msg_msg }
            mail_subject = msg_subject
            message = render_to_string(template, context)
            message_to = config('EMAIL_TO')
            email = EmailMessage(mail_subject, message, to=[message_to])
            email.content_subtype = 'html'
            email.send()
            print(f"\n# --- Form & Captcha were valid. More info: --- #\n{response_data}")
            return JsonResponse(response_data)
        else:
            return JsonResponse({'success': False, 'err_code': 'invalid_captcha'})
    else:
        return redirect('index')


#This method adds a new subscriber and send a confirmation mail
def subscribe(request):
    response_data = {}
    if request.POST.get('action') == 'subscribe_Form':
        subscribe_form = SubscribeForm(data=request.POST)
        if subscribe_form.is_valid():
            subscriber_email = request.POST.get('s_email')
            if not blog_subscriber.objects.filter(email=subscriber_email):
                rnd = generate_random_digits()
                conf_url ="{}?id={}".format(request.build_absolute_uri('/confirm/'), rnd)
                print(f'\n\n# --- PY: Confirmation URL: --- #\n{conf_url}')
                sub = blog_subscriber(email=subscriber_email, conf_num=rnd)
                sub.save()

                subj = 'Confirma tu email'
                template = 'LVR/mails/blog/confirm-mail.html'
                context = {'email': subscriber_email, 'confirmation_url': conf_url}

                # The 'mail_newsletter' method expects the following: message_to, subject, template, ctxt, is_massive):
                if mail_newsletter(subscriber_email, subj, template, context, False, request):
                    response_data['success'] = True
                else:
                    response_data['success'] = False
                    sub.delete()
                return JsonResponse(response_data)

            else:
                print(f'\n\n# --- PY: The email <<{subscriber_email}>> is already subscribed to newsletter --- #\n')
                return JsonResponse({'success': False, 'already_exists': True})        
        else:
            return JsonResponse({'success': False})        
    else:
        subscribe_form = SubscribeForm()



#This method notifies when a new post is accepted by superuser, so subscribers know when a new post is published (accepted) 
def notify_new(request):
    #Creating a subs object full of tuples with subscribers info from 'blog_subscriber' 
    subs = blog_subscriber.objects.values_list('email', 'conf_num').filter(confirmed=True)
    ctxt = []
    for sub in subs.iterator():
        lista=list(sub)
        ctxt.append(lista)
    subscribers = []
    print(f'\n\n# --- PY: (views.py) List of all subscribers email: --- #\n')
    for (i, element) in enumerate([i[0] for i in subs], start=1):
        subscribers.append(element)
        print(f'> {i}: {element}')

    print(subscribers)

    subj = 'Nuevo post en LVR: titulo del post'
    template = 'LVR/mails/blog/average-mail.html'
        
    if mail_newsletter(subscribers, subj, template, ctxt, True, request):
        print('Massive sent OK')
    else:
        print('Massive sent failed')



#Method that allows a subscriber confirm its email and receive updates
def confirm_subscribe(request):
    template = 'LVR/mails/blog/verify.html'
    conf_numb = request.GET['id']
    sub = blog_subscriber.objects.get(conf_num=conf_numb)
    context = {'email': sub.email}
    if sub.conf_num == conf_numb:
        sub.confirmed = True
        sub.save()
        print(f'\n\n# --- PY: The email <<{sub}>> is now confirmed! --- #\n')
        context['action'] = 'confirmed'
        return render(request, template, context)
    else:
        context['action'] = 'denied'
        return render(request, template, context)
    



#This method removes a subscriber from the database
def unsubscribe(request):
    template = 'LVR/mails/blog/verify.html'
    conf_numb = request.GET['id']
    context = {}
    if blog_subscriber.objects.filter(conf_num=conf_numb).exists():
        sub = blog_subscriber.objects.get(conf_num=conf_numb)
        if sub.conf_num == conf_numb:
            print(f'\n\n# --- PY: The email <<{sub.email}>> have been deleted from the database --- #\n')
            sub.delete()
            context['action'] = 'deleted'
            return render(request, template, context)
        else:
            return redirect('index')
    else:
        context['action'] = 'already_deleted'
        return render(request, template, context)

    

   
# ===========================#
# ====== Blog section ====== #
# ===========================#

#The homepage
def index(request):
    template_name = 'LVR/index.html'
    all_posts = blog_post.objects.filter(published_date__lte=timezone.now(), status=1).order_by('-published_date') #creating the 'all posts' variable, inside it we'll pass the result of the Query Set
    common_tags = blog_post.tags.most_common()[:3] #Getting the latest n trending tags
    trending = []
    for tag in common_tags:
        posts = blog_post.objects.filter(tags=tag, status=1) #Getting a QuerySet with all the posts that contains the common n tags
        for post in posts: #Accessing to each post inside the QuerySet
            if post not in trending:
                trending.append(post) #Putting that post inside the trending array list

    all_categories = blog_category.objects.all()
    avg = math.ceil(all_posts.count()/all_categories.count()) #Getting the average between all posts divided by number of categories
    popular_categories = blog_category.objects.annotate(post_count=Count('catego')).filter(post_count__gte=avg)
    #Once average is calculated, we filter categories that have more or equal posts (gte) than the average
    # print(f" categorias: {popular_categories}")
    diccionario = {}

    # TODO: while diccionario < 8 añadir

    for category in popular_categories:
        how_many = all_posts.filter(category=category).count() #Getting how many posts with that popular category exists
        diccionario[category]=how_many

    # print(diccionario)
    paginator = Paginator(all_posts, 9) #n posts in each page
    page = request.GET.get('page')
    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except EmptyPage:
        post_list = paginator.page(paginator.num_pages)
    context = { 'all_posts': all_posts, 'trending': trending[:3], 'page': page, 'post_list': post_list, 'popular_categories': diccionario }
    return render(request, template_name, context)



#This method shows the detail of the selected post of the blog
@check_recaptcha
def post_detail(request, category_text, slug_text):
    template = 'LVR/post_detail.html'
    post = get_object_or_404(blog_post, slug=slug_text)    
    get_author = post.author
    more_from_author = blog_post.objects.filter(author=get_author).order_by('-published_date')[:4]
    related = post.tags.similar_objects()[:3] #Getting the last 3 posts that contains the same tags that the current post
    all_comments = post.comments.filter(is_approved=True) # Filtering only approved comments
    new_comment = None
    response_data = {}

    if request.POST.get('action') == 'newCmt_Form':
        cmt_form = CommentForm(data=request.POST)
        if cmt_form.is_valid() and request.recaptcha_is_valid:
            print('\n\n# --- PY: Form & Captcha passed --- #')
            name = request.POST.get('author')
            email = request.POST.get('author_email')
            cmt = request.POST.get('comment_body')
            response_data['success'] = True
            response_data['cmt_name'] = name
            response_data['cmt_name'] = email
            response_data['cmt_name'] = cmt
            new_comment = cmt_form.save(commit=False) #Create a new comment but don't save it to the DB yet
            new_comment.in_post = post #Assign the current post to the comment
            new_comment.save()
            print(f"\n# --- Form & Captcha were valid. More info: --- #\n{response_data}")
            return JsonResponse(response_data)
        else:
            return JsonResponse({'success': False, 'err_code': 'invalid_captcha'})
    else:
        cmt_form = CommentForm()

    context = {
        'post': post,
        'related_posts': related,
        'more_from_author': more_from_author,
        'comments': all_comments,
        'new_comment': new_comment,
        'cmt_form': cmt_form
    }

    return render(request, template, context )





#All authors page
def authors(request):
    template = 'LVR/authors.html'
    all_authors = blog_author.objects.filter(activated_account=True).order_by('name')
    paginator = Paginator(all_authors, 20) #n authors in each page
    page = request.GET.get('page')
    try:
        authors = paginator.page(page)
    except PageNotAnInteger:
        authors = paginator.page(1)
    except EmptyPage:
        authors = paginator.page(paginator.num_pages)
    context = {'page': page, 'authors': authors, 'all_authors': all_authors }
    return render(request, template, context)





#Author detail
def author_detail(request, pinchiautor):
    template = 'LVR/author_detail.html'
    author = blog_author.objects.filter(slug=pinchiautor).first()
    posts_by_author = blog_post.objects.filter(author__slug=pinchiautor, status=1).order_by('-published_date')  #Getting al posts by the current author
    paginator = Paginator(posts_by_author, 9)
    page = request.GET.get('page')
    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except EmptyPage:
        post_list = paginator.page(paginator.num_pages)
    context = { 'author': author, 'page': page, 'post_list': post_list }
    return render(request, template, context)



#All Tags page
def tags(request):
    template = 'LVR/tags.html'
    all_tags = Tag.objects.all()
    #TO DO: If tag belongs to a non-approved post, hide that tag
    context = { 'all_tags': all_tags }
    return render(request, template, context)



# A particular tag page
def tags_detail(request, slug):
    template = 'LVR/tags_detail.html'
    tag = get_object_or_404(Tag, slug=slug)
    posts = blog_post.objects.filter(tags=tag, status=1)
    context = { 'tag': tag, 'posts': posts }
    return render(request, template, context)



# ALL categories page
def categories(request):
    template = 'LVR/categories.html'
    all_categories = blog_category.objects.all()
    diccionario = {}
    for category in all_categories:
        how_many = blog_post.objects.filter(category=category, status=1).count() #Getting how many posts with that popular category exists
        diccionario[category]=how_many
    context = { 'categories': diccionario }
    return render(request, template, context)



# A particular category page
def categories_detail(request, slug):
    template = 'LVR/categories_detail.html'
    category = get_object_or_404(blog_category, slug=slug)
    posts = blog_post.objects.filter(category=category, status=1)
    context = { 'category': category, 'posts': posts}
    return render(request, template, context)



#About page
def about(request):
    return render (request, 'LVR/about.html')



#Custom error 404 http states
def page_not_found_404(request, exception):
    return render (request, 'LVR/http_states/404.html', {})




# ===================================#
#  ===== Miscellaneous section ===== #
# ===================================#


def cookies(request):
    template =  'LVR/misc/cookies.html'
    cookies = blog_misc.objects.filter(Q(name__contains="cookies")|Q(head_desc__contains="cookies")).first()
    context = { 'misc': cookies }
    return render(request, template, context)



def privacy_policy(request):
    template =  'LVR/misc/privacy_policy.html'
    privacy = blog_misc.objects.filter(Q(name__contains="privacidad")|Q(head_desc__contains="privacidad")).first()
    context = { 'misc': privacy }
    return render(request, template, context)



def service_terms(request):
    template =  'LVR/misc/service_terms.html'
    service = blog_misc.objects.filter(Q(name__contains="servicio")|Q(head_desc__contains="servicio")).first()
    context = { 'misc': service }
    return render(request, template, context)



def comments_terms(request):
    template =  'LVR/misc/comment_terms.html'
    cmt = blog_misc.objects.filter(Q(name__contains="comunidad")|Q(head_desc__contains="comunidad")).first()
    context = { 'misc': cmt }
    return render(request, template, context)



@login_required(login_url='login')
def rules(request):
    template =  'LVR/misc/rules.html'
    rules = blog_misc.objects.filter(Q(name__contains="escritura")|Q(head_desc__contains="escritura")).first()
    context = { 'misc': rules }
    return render(request, template, context)




# ==================================#
# ====== User/Author section ====== #
# ==================================#



def login(request):
    template = 'LVR/user/login.html'
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        if request.method == 'POST':
            username = request.POST.get('A_username')
            password = request.POST.get('A_password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                do_login(request, user)
                return redirect('dashboard')
            else:
                messages.info(request, _('WrongUserOrPass'))
    context = {}
    return render(request, template, context)



@login_required(login_url='login')
def dashboard(request):
    template = 'LVR/user/dashboard.html'
    author = blog_author.objects.filter(name=request.user).first()
    posts_by_author = blog_post.objects.filter(author=author).order_by('-published_date')
    context = { 'author': author, 'posts_by_author': posts_by_author}
    return render (request, template , context)



@login_required(login_url='login')
def profile(request):
    author = blog_author.objects.filter(name=request.user).first()

    total_post_list = blog_post.objects.filter(author=author).count()
    draft_posts = blog_post.objects.filter(author=author, status=0).count()
    approved_posts = blog_post.objects.filter(author=author, status=1).count()
    rejected_posts = blog_post.objects.filter(author=author, status=2).count()
    archived_posts = blog_post.objects.filter(author=author, status=3).count()

    context = {
        'author': author,
        'total_posts': total_post_list,
        'draft': draft_posts,
        'approved': approved_posts,
        'rejected': rejected_posts,
        'archived': archived_posts,
    }
    return render (request, 'LVR/user/profile.html', context)



@login_required(login_url='login')
def calendar(request):
    template = 'LVR/user/calendar.html'
    author = blog_author.objects.get(name=request.user)
    context = { 'author': author}
    return render (request, template, context)



@login_required(login_url='login')
def settings(request):
    template = 'LVR/user/settings.html'
    author = blog_author.objects.get(name=request.user)
    perms = request.user.get_group_permissions()
    context = { 'author': author, 'permissions': perms}
    return render (request, template, context)



def send_activation_link(user, user_email, first_name, last_name, domain):
    template = 'LVR/user/aa-email-sent.html'
    try:
        uid = urlsafe_base64_encode(force_bytes(user.id))
        token = account_activation_token.make_token(user)
        url = domain + reverse('activate', kwargs={ 'uidb64':uid, 'token':token })
        mail_subject = _('EmailWelcome_Subject')+first_name+' '+last_name
        message = render_to_string('LVR/user/aa-activate-email.html', {
            'name': first_name,
            'user': user,
            'url':url,
            'uid': uid,
            'token': token
            })
        message_to = user_email
        email = EmailMessage(mail_subject, message, to=[message_to])
        email.content_subtype = 'html'
        email.send()
        print('Email sent successfully')
        return True
    except:
        print('The email was not sent')
        return False
    print('reached2')
    return None




@login_required(login_url='login')
@user_passes_test(lambda u: u.is_superuser)
def sign_up(request):
    template = 'LVR/user/sign_up.html'
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False #Preventing non-confirmed users to login
            user.save()
            # user = form.cleaned_data.get('username')
            # messages.success(request, 'Account ' + user + ' created successfully')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            user_email = form.cleaned_data.get('email')
            domain = get_current_site(request).domain
            template = 'LVR/user/aa-email-sent.html'
            sent_successfully = False
            context = {'email': user_email, 'first_name': first_name, 'last_name': last_name, 'sent_successfully': sent_successfully }

            if send_activation_link(user, user_email, first_name, last_name, domain):
                context['sent_successfully']=True # Updating the value 'sent_successfully' to True in the 'context' dictionary
                rendered = render_to_string(template, context)
                return HttpResponse(rendered)
            else:
                rendered = render_to_string(template, context)
                user.delete()
                return HttpResponse(rendered)
        else:
            messages.error(request, _('ErrorCreatingUser') )
    context = {'form': form}
    return render (request, template, context)



@login_required(login_url='login')
@user_passes_test(lambda u: u.is_superuser)
def approve_post(request):
    return redirect('dashboard')
    
    



def signup_account_activated(request, user):
    template = 'LVR/user/aa-account-activated.html'
    context = {'new_user': user}
    return render(request, template, context)



def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.refresh_from_db()
        user.is_active = True
        user.blog_author.activated_account = True
        toslug = user.first_name + ' ' + user.last_name
        user.blog_author.slug = slugify(toslug)
        user.blog_author.email = user.email
        # The user is being activated now, so in previous line we take meanwhile the private email and set it as the public one - can be changed later in settings
        user.save()
        return redirect('account_activated', user=user)
    else:
        template = 'LVR/user/aa-wrong-link.html'
        rendered = render_to_string(template, {'user': user } )
        return HttpResponse(rendered)



#This method allows user/author add a new post
@login_required(login_url='login')
def post_list(request):
    template = 'LVR/user/post_list.html'
    author = blog_author.objects.filter(name=request.user).first()
    post_list = blog_post.objects.filter(author=author, status=2).order_by('-published_date')
    context = { 'author': author, 'post_list': post_list}
    return render(request, template, context)



#This method allows user/author add a new post
@login_required(login_url='login')
def post_new(request):
    template = 'LVR/user/post_edit.html'
    if request.method == "POST":
        newPost_form = PostForm(request.POST, request.FILES)
        if newPost_form.is_valid():
            newpost = newPost_form.save(commit=False)
            get_author = blog_author.objects.get(name=request.user)
            newpost.author = get_author
            newpost.published_date = timezone.now()
            newpost.save()
            newPost_form.save_m2m()
            messages.success(request, _('PostCreated_Ok'))
            return redirect('post_detail', category_text=newpost.category, slug_text=newpost.slug)
    else:
        newPost_form = PostForm()
    context = { 'newPost_form': newPost_form }
    return render(request, template, context)



#This method opens a text editor for edit an existing post
@login_required(login_url='login')
def post_edit(request, slug_text):
    template = 'LVR/user/post_edit.html'
    post = get_object_or_404(blog_post, slug=slug_text)
    is_edit = True
    status = post.status
    slug = post.slug
    title = post.title
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            get_author = blog_author.objects.get(name=request.user)
            post.author = get_author
            post.published_date = timezone.now()
            post.status = 0
            post.save()
            form.save_m2m()
            # messages.success(request, _('PostUpdated_Ok'))
            return redirect('post_detail', category_text=newpost.category, slug_text=post.slug)
    else:
        form = PostForm(instance=post)
    context = {'form': form, 'is_edit': is_edit, 'status': status, 'title': title, 'slug': slug }
    return render (request, template, context)



@login_required(login_url='login')
def post_delete(request, slug_text):
    post = get_object_or_404(blog_post, slug=slug_text)
    post.delete()
    return redirect('dashboard')



@login_required(login_url='login')
def post_archive(request, slug_text):
    post = get_object_or_404(blog_post, slug=slug_text)
    post.status = 3
    post.save()
    return redirect('dashboard')



def send_newsletter_msg(request):
    return redirect('dashboard')
    



def logout(request):
    do_logout(request)
    # Login redirect, implement later a variable to allow user decide if go to login or index
    return redirect('index')




