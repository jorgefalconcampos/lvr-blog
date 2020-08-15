from django.utils import timezone
import datetime, math, json, urllib, smtplib
from django.template.defaultfilters import date
from django.contrib.auth.models import User
from django.core import serializers, mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404, HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.shortcuts import redirect, render, get_object_or_404, reverse
from . models import blog_post, blog_category, blog_author, blog_postComment, blog_crew, blog_misc, blog_subscriber  #Importing the models
from . forms import PostForm, CommentForm, CreateUserForm, AccountEditUserForm, ProfileEditUserForm, ProfileEditAuthorForm, ContactForm, SubscribeForm, NewCategory, SearchForm
from django.utils.translation import gettext as _
from django.conf import settings as conf_settings #To read reCaptcha's key
from . decorators import check_recaptcha
from . helpers import generate_random_digits, mail_newsletter
from taggit.models import Tag
from django.db.models import Count, Q, F
from django.db.models.functions import Upper
from decouple import config
from django.views.decorators.http import require_GET

#User, Admin & Superuser
from django.utils.text import slugify
from django.contrib import messages #To customize login & signup forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate, login as do_login, logout as do_logout
from django.contrib.auth.decorators import login_required, user_passes_test # upt is to restrict to super user only
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.template.loader import render_to_string
from . tokens import account_activation_token
from django.core.mail import EmailMessage, get_connection, send_mail
from django.core.mail.backends.smtp import EmailBackend
from django.contrib.auth.tokens import default_token_generator
# from LeVeloRouge.settings import NEMAIL_HOST_USER




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
    return render(request, template, context)

def cm(request):
    # notify_new(request)
    # return render(request, 'LVR/user/contact-mail.html', {})
    # context = {'action': 'deleted'}
    # return render(request, 'LVR/mails/blog/confirm-mail.html')

    # return render(request, 'LVR/mails/user/pswd/reset-pass-mail.html')
    # return render(request, 'LVR/user/pswd/password-reset-done.html')
    # return render(request, 'LVR/user/pswd/password-reset-complete.html')


    # return render(request, 'LVR/mails/user/pswd/reset-pass.html')

    return render(request, 'LVR/mails/user/wrong-link.html')



    # return render(request, 'LVR/mails/blog/verify.html')



#For searching a blog_post object
def search(request):
    template = 'LVR/search.html'

    if request.method == 'GET':
        search_term = request.GET.get('q')
        bad_query = False
        bad_query_len = False 

        if not search_term:
            return render(request, template, {'empty_search':True})

        if len(search_term) <= 2:
            bad_query = True
        elif len(search_term) > 50:
            bad_query_len = True 
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
    return render(request, template, {'bad_query':bad_query, 'bad_query_len':bad_query_len} )



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

    # all_osts = str(all_posts.count()) #counting all-time posts
    # print(f"TODOS LOS POSTS: {all_osts}")

    common_tags = blog_post.tags.most_common()[:3] #Getting the latest n trending tags
    trending = []
    for tag in common_tags:
        posts = blog_post.objects.filter(tags=tag, status=1) #Getting a QuerySet with all the posts that contains the common n tags
        for post in posts: #Accessing to each post inside the QuerySet
            if post not in trending:
                trending.append(post) #Putting that post inside the trending array list

    all_categories = blog_category.objects.all()

    try:
        avg = math.ceil(all_posts.count()/all_categories.count()) #Getting the average between all posts divided by number of categories
        popular_categories = blog_category.objects.annotate(post_count=Count('catego')).filter(post_count__gte=avg)
        #Once average is calculated, we filter categories that have more or equal posts (gte) than the average
        # print(f" categorias: {popular_categories}")
        diccionario = {}
        for category in popular_categories:
            how_many = all_posts.filter(category=category).count() #Getting how many posts with that popular category exists
            if len(diccionario) < 8:
                diccionario[category]=how_many
    except Exception as e:
        diccionario = {}

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

    # if post isn't approved yet, only the author and superuser can see it in detail, otherwise redirect to index
    # if post.status != 1:
    #     if not ((request.user == post.author.name) or (request.user.is_superuser)):
    #         return redirect('index')

    more_from_author = blog_post.objects.filter(author=post.author, status=1).exclude(slug=post.slug).order_by('-published_date')[:3]
    related = post.tags.similar_objects()[:3] #Getting the last 3 posts that contains the same tags that the current post
    all_comments = post.comments.filter(is_approved=True) # Filtering only approved comments
    new_comment = None
    response_data = {}
    response_data_r = {'success': True}

    # if request.POST.get('action') == 'reaction_Form':
    #     try:
    #         if request.POST.get('reaction') == 'fav':
    #             post.vote_fav = F('vote_fav')+1
    #         elif request.POST.get('reaction') == 'util':
    #             post.vote_util = F('vote_util')+1
    #         elif request.POST.get('reaction') == 'thumbs_up':
    #             post.vote_tmbup = F('vote_tmbup')+1
    #         elif request.POST.get('reaction') == 'thumbs_down':
    #             post.vote_tmbdn = F('vote_tmbdn')+1
    #     except:
    #         response_data_r['success'] = False
    #     finally:
    #         post.save()
    #         return JsonResponse(response_data_r)

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
    details = []
    all_authors = blog_author.objects.filter(activated_account=True).order_by('name__first_name', 'name__last_name')
    for author in all_authors:
        dicc = {}
        num = blog_post.objects.filter(author=author, status=1).count()
        dicc['author'] = author
        dicc['posts'] = num
        details.append(dicc)
    paginator = Paginator(details, 9) #n authors in each page
    page = request.GET.get('page')
    try:
        authors_list = paginator.page(page)
    except PageNotAnInteger:
        authors_list = paginator.page(1)
    except EmptyPage:
        authors_list = paginator.page(paginator.num_pages)
    context = {'page': page, 'authors_list': authors_list}
    return render(request, template, context)





#Author detail
def author_detail(request, pinchiautor):
    template = 'LVR/author_detail.html'
    author = get_object_or_404(blog_author, slug=pinchiautor)
    posts_by_author = blog_post.objects.filter(author__slug=pinchiautor, status=1).order_by('-published_date')  #Getting al posts by the current author
    paginator = Paginator(posts_by_author, 5)
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
    posts = blog_post.objects.filter(tags=tag, status=1).order_by('-published_date')
    paginator = Paginator(posts, 6)
    page = request.GET.get('page')
    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except EmptyPage:
        post_list = paginator.page(paginator.num_pages)
    context = { 'tag': tag, 'posts': posts, 'post_list': post_list }
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
    posts = blog_post.objects.filter(category=category, status=1).order_by('-published_date')
    paginator = Paginator(posts, 6)
    page = request.GET.get('page')
    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except EmptyPage:
        post_list = paginator.page(paginator.num_pages)

    context = { 'category': category, 'posts': posts, 'post_list': post_list}
    return render(request, template, context)



#About page
def about(request):
    crew = blog_crew.objects.all()
    context = { 'crew': crew}
    return render (request, 'LVR/about.html', context)



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
        if request.POST.get('action') == 'login_Form':
            username = request.POST.get('username')
            password = request.POST.get('password')
            if (username and password):
                user = authenticate(request, username=username, password=password)
                if user is not None and user.is_active:
                    do_login(request, user)

                    # return HttpResponse(json.dumps({'status': True}), content_type='application/json')
                    return JsonResponse({'status': True})
                    # return redirect('dashboard')
                else:
                    return JsonResponse({'status': False, 'err_code': 'login_failed'})
            else:
                return JsonResponse({'status': False, 'err_code': 'invalid_form'})
    context = {}
    return render(request, template, context)



@login_required(login_url='login')
def dashboard(request):
    template = 'LVR/user/dashboard.html'
    author = blog_author.objects.filter(name=request.user).first()
    posts_by_author = blog_post.objects.filter(author=author).order_by('-created_date')[:5]
    context = { 'author': author, 'posts_by_author': posts_by_author}
    return render (request, template , context)



@login_required(login_url='login')
def profile(request):
    author = blog_author.objects.filter(name=request.user).first()
    total_post_list = blog_post.objects.filter(author=author)
    posts = {'approved':0, 'draft':0, 'archived':0, 'rejected':0}
    reactions = {'fav':0, 'util':0, 'tmbup':0, 'tmbdn':0}

    for post in total_post_list:
        if post.status == 0:
            posts['draft'] += 1
        elif post.status == 1:
            posts['approved'] += 1
            reactions['fav'] += post.vote_fav
            reactions['util'] += post.vote_util
            reactions['tmbup'] += post.vote_tmbup
            reactions['tmbdn'] += post.vote_tmbdn
        elif post.status == 2:
            posts['rejected'] += 1
        elif post.status == 2:
            posts['archived'] += 1

    total_reactions = sum([int(i) for i in reactions.values()])

    context = {'author': author, 'posts': posts, 'total_posts': total_post_list.count(), 'reactions': reactions, 'total_reactions': total_reactions}
    return render (request, 'LVR/user/profile.html', context)



@login_required(login_url='login')
@user_passes_test(lambda u: u.is_superuser)
def new_category(request):
    template = 'LVR/user/new_category.html'
    response_data = {'success': False}
    if request.method == 'POST':
        form = NewCategory(data=request.POST, files=request.FILES)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            if not blog_category.objects.filter(slug=slugify(name)).exists():
                newCateg = form.save(commit=False)
                newCateg.save()
                form.save_m2m()
                response_data['success'] = True
                return JsonResponse(response_data)
            else:
                response_data['err_code'] = 'already_exists'
                return JsonResponse(response_data)
        else:
            response_data['err_code'] = form.errors
            return JsonResponse(response_data)
    else:
        form = NewCategory()
    context = {'newCategoryForm':form}
    return render(request, template, context)




@login_required(login_url='login')
def calendar(request):
    template = 'LVR/user/calendar.html'
    author = blog_author.objects.get(name=request.user)
    context = { 'author': author}
    return render (request, template, context)



@login_required(login_url='login')
def notifications(request):
    template = 'LVR/user/notifications.html'
    context = {}
    return render (request, template, context)



@login_required(login_url='login')
def tasks(request):
    template = 'LVR/user/tasks.html'
    context = {}
    return render (request, template, context)



@login_required(login_url='login')
def settings(request):
    template = 'LVR/user/settings.html'
    author = blog_author.objects.get(name=request.user)

    response_data = {}

    if request.POST.get('action') == 'profile_Form':
        profile_user_form = ProfileEditUserForm(data=request.POST, instance=request.user)
        profile_author_form = ProfileEditAuthorForm(data=request.POST, instance=author, files=request.FILES)
        if  profile_user_form.is_valid() and profile_author_form.is_valid():
            prof_user = profile_user_form.save(commit=False)
            prof_user.save()
            prof_author = profile_author_form.save(commit=False)
            prof_author.save()
            response_data['success'] = True
            return JsonResponse(response_data)
        else:
            return JsonResponse({'success': False})
    else:
        profile_user_form = ProfileEditUserForm(instance=request.user)

    if request.POST.get('action') == 'account_Form':
        acc_form = AccountEditUserForm(request.POST, instance=request.user)
        if acc_form.is_valid():
            if not User.objects.filter(email=request.POST.get('email')).count() > 0:
                acc_form.save()
                response_data['success'] = True
                return JsonResponse(response_data)
            else:
                return JsonResponse({'success': False, 'errors': 'email_already_taken'})
        else:
            return JsonResponse({'success': False, 'errors': acc_form.errors})
    else:
        acc_form = AccountEditUserForm(instance=request.user)

    account_frm_initial = { 'username': request.user, 'email': request.user.email }
    profile_frm_user_initial = { 'first_name': request.user.first_name, 'last_name': request.user.last_name }
    profile_frm_author_initial = { 'title': author.title, 'bio': author.bio, 'email': author.email, 'image':author.image, 'facebook_URL': author.facebook_URL, 'twitter_URL': author.twitter_URL, 'linkedin_URL': author.linkedin_URL }

    context = {
        'author': author,
        'AccountForm': AccountEditUserForm(initial=account_frm_initial),
        # --------------------- #
        'ProfileUserForm': ProfileEditUserForm(initial=profile_frm_user_initial),
        'ProfileAuthorUserForm': ProfileEditAuthorForm(initial=profile_frm_author_initial),
    }

    print(author.slug)


    if not request.user.is_superuser:
        avg_user_perms = ['Crear posts en mi nombre', 'Editar posts en mi nombre', 'Archivar posts escritos en mi nombre', 'Eliminar posts escritos en mi nombre', 'Solicitar cambio de contraseña', 'Solicitar restablecimiento de contraseña', 'Crear tags (al crear un post, si el tag no existe)', 'Modificar datos personales públicos', 'Modificar datos personales privados', 'Cambiar imagen de perfil público', 'Login y logout']
        context['permissions'] = avg_user_perms
    else:
        perms = request.user.get_group_permissions()
        context['permissions'] = perms


    return render (request, template, context)




@login_required(login_url='login')
def edit_account_info(request):
    if request.method == 'POST':
        form = EditUserForm(instance=request.user)

        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = EditUserForm(isinstance=request.user)
        context = { 'form':form }
        return render(reques, 'LVR/user/settings.html', context)




def send_activation_link(user, user_email, first_name, last_name, domain):
    template = 'LVR/mails/user/activate-email.html'
    try:
        uid = urlsafe_base64_encode(force_bytes(user.id))
        token = account_activation_token.make_token(user)
        url = domain + reverse('activate', kwargs={ 'uidb64':uid, 'token':token })
        mail_subject = _('EmailWelcome_Subject')+first_name+' '+last_name
        message = render_to_string(template, {
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
            template = 'LVR/mails/user/email-sent.html'
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
def moderate_posts(request):
    template = 'LVR/user/moderate_posts.html'
    all_post_list = blog_post.objects.filter(status=0).order_by('-created_date')
    paginator = Paginator(all_post_list, 10)
    page = request.GET.get('page')
    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except EmptyPage:
        post_list = paginator.page(paginator.num_pages)
    context = {'post_list': post_list}
    return render(request, template, context)



# This method deletes, archives or rejects a blog post - Only superuser can reject
@login_required(login_url='login')
def post_actions(request, post_action, pk):
    response_data = {'success': False}
    post = blog_post.objects.filter(pk=pk).first()
    if request.user.is_authenticated:
        try:
            if request.user == post.author.name:
                if post_action == 'delete':
                    post.delete()
                    response_data['success'] = True
                elif post_action == 'archive':
                    post.archive_post()
                    response_data['success'] = True
                elif post_action == 'unarchive':
                    post.unarchive_post()
                    response_data['success'] = True
            elif request.user.is_superuser:
                if post_action == 'reject':
                    post.reject_post()
                    response_data['success'] = True
                elif post_action == 'approve':
                    post.approve_post()
                    response_data['success'] = True
            else: 
                response_data['invalid_request'] = f"{request.user} cannot perform this action - is not the author"
        except Exception as e:
            response_data['err'] = str(e)
        finally:
            return JsonResponse(response_data)
    else:
        return redirect('index')
 



def signup_account_activated(request, user):
    template = 'LVR/mails/user/account-activated.html'
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
        template = 'LVR/mails/user/wrong-link.html'
        rendered = render_to_string(template, {'user': user } )
        return HttpResponse(rendered)


#This method show all the posts written by user/author
@login_required(login_url='login')
def post_list(request):
    template = 'LVR/user/post_list.html'
    author = blog_author.objects.filter(name=request.user).first()
    all_post_list = blog_post.objects.filter(author=author).order_by('-published_date')
    paginator = Paginator(all_post_list, 10)
    page = request.GET.get('page')
    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except EmptyPage:
        post_list = paginator.page(paginator.num_pages)

    context = { 'author': author, 'post_list': post_list}
    return render(request, template, context)



#This method allows user/author add a new post
@login_required(login_url='login')
def post_new(request):
    template = 'LVR/user/post_edit.html'
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            newpost = form.save(commit=False)
            get_author = blog_author.objects.get(name=request.user)
            newpost.author = get_author
            newpost.published_date = timezone.now()
            newpost.save()
            form.save_m2m()
            # messages.success(request, _('PostCreated_Ok'))
            return redirect('post_detail', category_text=newpost.category, slug_text=newpost.slug)
        else:
            messages.error(request, _('EmptyFields'))
    else:
        form = PostForm()
    context = { 'postForm': form }
    if not blog_category.objects.count():
        context['nocategs'] = True
    return render(request, template, context)



#This method opens a text editor for edit an existing post
@login_required(login_url='login')
def post_edit(request, slug_text):
    template = 'LVR/user/post_edit.html'
    post = get_object_or_404(blog_post, slug=slug_text)
    status = post.status
    slug = post.slug
    title = post.title
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post, files=request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            get_author = blog_author.objects.get(name=request.user)
            post.author = get_author
            post.published_date = timezone.now()
            post.status = 0
            post.save()
            form.save_m2m()
            return redirect('post_detail', category_text=post.category, slug_text=post.slug)
    else:
        form = PostForm(instance=post)
    context = {'postForm': form, 'is_edit': True, 'post':post }
    return render (request, template, context)




@login_required(login_url='login')
def post_delete(request, pk):
    response_data = {'success': False}
    try:
        post = blog_post.objects.filter(pk=pk).first()
        if request.user == post.author.name:
            post.delete()
            response_data['success'] = True
        else: 
            response_data['invalid_request'] = f"{request.user} cannot perform this action - is not the author"
    except Exception as e:
        response_data['err'] = str(e)
    finally:
        return JsonResponse(response_data)



@login_required(login_url='login')
def post_archive(request, pk):
    response_data = {'success': False}
    try:
        post = blog_post.objects.filter(pk=pk).first()
        if request.user == post.author.name:
            post.status = 3
            post.save()
            response_data['success'] = True
        else: 
            response_data['invalid_request'] = f"{request.user} cannot perform this action - is not the author"
    except Exception as e:
        response_data['err'] = str(e)
    finally:
        return JsonResponse(response_data)











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




