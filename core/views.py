from __future__ import unicode_literals
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .forms import UserCreationForm, NameUpdateForm
from .tokens import account_activation_token
from django.contrib.auth import login, update_session_auth_hash, REDIRECT_FIELD_NAME
import itertools
from django.utils.text import slugify
from .models import User, Profile, Titles, Comments, Topic, Url, Customtopic, Blog, Blogpic, Titlesprop, Subtopic
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.views import login as auth_views_login
from django.contrib.auth import authenticate as auth_views_authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from . import forms
from django.http import Http404, JsonResponse, HttpResponse
from django.core.serializers import serialize
import json
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.forms import AuthenticationForm
from django.http.response import HttpResponseForbidden
from . documents import search
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Create your views here.


def is_writer(user):
    return user.profile.is_writer

def signup(request):
    reactivation = 'no'
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        active_users = User._default_manager.filter(**{
                '%s__iexact' % User.get_email_field_name(): request.POST.get('email'),
                'is_active' : False,
            })
        if active_users:
            reactivation = 'yes'
        else:
            reactivation = 'no'
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate Your Streams Account'
            message = render_to_string('core/account_activation_email.html', {
                'user' : user,
                'domain' : current_site.domain,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token' : account_activation_token.make_token(user),
                })
            user.email_user(subject, message)
            return redirect('core:account_activation_sent')
    else:
        form = UserCreationForm()
    return render(request, 'core/signup.html', {
        'form' : form,
        'reactivate' : reactivation
        })

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        max_length = User._meta.get_field('slug').max_length
        user.slug = orig = slugify("%s %s" % (user.first_name, user.last_name))[:max_length]
        for x in itertools.count(1):
            if not User.objects.filter(slug=user.slug).exists():
                break
            user.slug = "%s-%d" % (orig[:max_length-len(str(x))-1], x)
        user.profile.save()
        user.save()
        login(request, user)
        return redirect('core:home')
    else:
        return render(request, 'core/account_activation_invalid.html')

def account_activation_sent(request):
    return render(request, 'core/account_activation_sent.html')

def resend_account_activation(request):
    if request.method == 'POST':
        form = forms.ResendActivationLinkForm(request.POST)
        if form.is_valid():
            active_users = User._default_manager.filter(**{
                '%s__iexact' % User.get_email_field_name(): form.cleaned_data['email'],
                'is_active' : False,
            })
            if active_users:
                current_site = get_current_site(request)
                subject = 'Activate Your Streamsources Account'
                message = render_to_string('core/account_activation_email.html', {
                    'user' : active_users[0],
                    'domain' : current_site.domain,
                    'uid' : urlsafe_base64_encode(force_bytes(active_users[0].pk)).decode(),
                    'token' : account_activation_token.make_token(active_users[0]),
                })
                active_users[0].email_user(subject, message)
                return redirect('core:account_activation_sent')
    form = forms.ResendActivationLinkForm()
    return render(request, 'core/account_activation_resend.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('core:change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'core/change_password.html', {
        'form' : form
        })

def Home(request, *args, **kwargs):
    blogs_list = Titles.objects.filter(is_published=True).filter(is_approved=True).order_by('-time_published')
    page = request.GET.get('page',1)
    paginator = Paginator(blogs_list, 15)
    try:
        blogs = paginator.page(page)
    except PageNotAnInteger:
        blogs = paginator.page(1)
    except EmptyPage:
        blogs = paginator.page(paginator.num_pages)

    topics = Topic.objects.all()
    return render(request, 'core/home.html', {
        'blogdata' : blogs,
        'topics' : topics
        })

def profile(request, args):
    profile = get_object_or_404(User, slug=args)
    count = None
    if profile.profile.is_writer or request.user == profile:
        if profile.profile.is_writer:
            titles = Titles.objects.filter(user=profile).filter(is_published=False)
            count = titles.count()
        return render(request, 'core/profile.html', {
        'profile' : profile,
        'count' : count
        })
    raise Http404()


@login_required
def edit_name(request):
    form = NameUpdateForm(instance=request.user)
    if request.method == "POST":
        form = NameUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
        return redirect('core:profile', request.user.slug)
    return render(request, 'core/name.html', {
        'form' : form
        })

@login_required
def edit_location(request):
    form = forms.LocationUpdateForm(instance=request.user.profile)
    if request.method == "POST":
        form = forms.LocationUpdateForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
        return redirect('core:profile', request.user.slug)
    return render(request, 'core/location.html', {
        'form' : form
        })

@login_required
def edit_bio(request):
    form = forms.BioUpdateForm(instance=request.user.profile)
    if request.method == "POST":
        form = forms.BioUpdateForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
        return redirect('core:profile', request.user.slug)
    return render(request, 'core/bio.html', {
        'form' : form
        })

@login_required
def update_propic(request):
    user = request.user
    form = forms.ImageUpdateForm(request.POST, request.FILES)
    if request.method == "POST":
        form = forms.ImageUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if not user.profile.image == 'profile/img.png':
            user.profile.image.delete()
        if form.is_valid():
            form.save()
        return redirect('core:profile', request.user.slug)
    return render(request, 'core/image.html', {
        'form' : form
        })
@login_required
def remove_propic(request):
    user = request.user
    if not user.profile.image == 'profile/img.png':
        user.profile.image.delete()
        user.profile.image = 'profile/img.png'
        user.save()
    return redirect('core:profile', request.user.slug)

@login_required
@user_passes_test(is_writer)
def create_blogs(request):
    return render(request, 'core/create_blog.html')

@login_required
@user_passes_test(is_writer)
def create_title(request):
    form = forms.TitlesForm()
    if request.method == 'POST':
        form = forms.TitlesForm(request.POST)
        if form.is_valid():
            created_title = form.save(commit=False)
            created_title.user = request.user
            max_length = Titles._meta.get_field('slug').max_length
            created_title.slug = orig = slugify(created_title.title)[:max_length]
            for x in itertools.count(1):
                if not Titles.objects.filter(slug=created_title.slug).exists():
                    break
                created_title.slug = "%s-%d" % (orig[:max_length-len(str(x))-1], x)
            created_title.save()
            args = get_object_or_404(Titles, slug=created_title.slug).pk
            return redirect('core:blogpost', args)
    return render(request, 'core/create_title.html', {
        'form' : form
        })

@login_required
@user_passes_test(is_writer)
def create_title_cover(request, args):
    title = get_object_or_404(Titles, pk=args)
    if request.user == title.user:
        form = forms.TitlesCoverForm(request.POST, request.FILES)
        if form.is_valid():
            s = title.coverpic_set.all()
            if s is not None:
                for i in s:
                    i.delete()
            cover = form.save(commit=False)
            cover.title = title
            cover.save()
            return JsonResponse({})
        return JsonResponse({})
    raise Http404()

@login_required
@user_passes_test(is_writer)
def create_content(request, args):
    title = get_object_or_404(Titles, pk=args)
    if title.user == request.user:
        data = get_content(title)
        return render(request, 'core/create_content.html', {
            'title' : title,
            'args' : args,
            'data' : data
            })
    raise Http404()

@login_required
@user_passes_test(is_writer)
def my_blogs(request):
    blogs = Titles.objects.filter(user=request.user)
    blogs_t = blogs.filter(is_published=True)
    blogs_f = blogs.filter(is_published=False)
    return render(request, 'core/myblogs.html', {
        'blogs_t' : blogs_t,
        'blogs_f' : blogs_f
        })

@login_required
@user_passes_test(is_writer)
def publish(request, args):
    title = get_object_or_404(Titles, pk=args)
    if title.user == request.user:
        if title.is_published:
            title.is_published = False
            title.save()
        else:
            title.is_published = True
            title.save()
        return redirect('core:myblogs')
    raise Http404()

def blog_index(request):
    blogs = Titles.objects.filter(is_published=True).order_by('-time_published')
    profile = User.objects.get(email='tuenylukejoseph@gmail.com')
    topics = Topic.objects.all()
    return {
    'blogdata': blogs,
    'profile' : profile,
    'topics' : topics
    }

def blog_display(request, name, args):
    title = get_object_or_404(Titles, slug=args)
    topic = title.customtopic
    if topic:
        titles = topic.titles_set.all().order_by('time_published')
    else:
        titles = None
    if title.is_published and title.is_approved:
        comments = Comments.objects.filter(title=title).order_by('-datetime')
        raw_form = forms.CommentsForm()
        form = UserCreationForm()
        if request.user.is_authenticated and request.user != title.user:
            title.authenticated_views = title.authenticated_views + 1
            title.total_views = title.total_views + 1
            title.save()
        elif request.user !=  title.user:
            title.total_views = title.total_views + 1
            title.save()
        data_tiny = Blog.objects.filter(title=title).last()
        return render(request, 'core/display.html', {
             'title' : title,
             'content' : data_tiny,
             'raw_form' : raw_form,
             'comments' : comments,
             'form' : form,
             'topic' : topic,
             'titles' :titles,
             })
    raise Http404()

@login_required
def add_comment(request, slug):
    data = {}
    if request.method == 'POST':
        comment = request.POST.get('comment', None)
        slug = request.POST.get('slug', None)
        title = get_object_or_404(Titles, slug=slug)
        comment_post = Comments(title=title, comment=comment, user=request.user)
        comment_post.save()
        data['comment'] = comment
        data['name'] = request.user.first_name
        data['slug'] = slug
        data['pk'] = comment_post.pk
        data['image'] = request.user.profile.image
        data['time'] = comment_post.datetime
        html_form = render_to_string('core/comment.html', data, request=request)
    return JsonResponse({'html_form' : html_form})


@login_required
def reply_comment(request, pk):
    form = forms.ReplyForm()
    context = {'form' : form, 'pk' : pk}
    if request.method == 'POST':
        data = {}
        content = request.POST.get('comment', None)
        pk = request.POST.get('pk', None)
        reply = get_object_or_404(Comments, pk=pk)
        title = reply.title
        comment_post = Comments(title=title, comment=content, user=request.user, reply=reply)
        comment_post.save()
        new_pk = comment_post.pk
        data['comment'] = content
        data['name'] = request.user.first_name
        data['pk'] = pk
        data['new_pk'] = new_pk
        data['image'] = request.user.profile.image
        data['time'] = comment_post.datetime
        html_form = render_to_string('core/add_reply.html', data, request=request)
        return JsonResponse({
            'html_form' : html_form,
            'pk' : pk
            })
    else:
        html_form = render_to_string('core/reply.html', context, request=request)
    return JsonResponse({
        'html_form' : html_form,
        'pk' : pk
        })

@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comments, pk=pk)
    if request.user == comment.user or comment.title.user:
        reply = comment.comments_set.all()
#        for r in reply:
#            r.delete()
        comment.delete()
        data = {'pk' : pk}
        return JsonResponse(data)
    raise Http404()

@login_required
def users(request):
    admin = User.objects.get(email='tuenylukejoseph@gmail.com')
    if request.user == admin:
        users = User.objects.all()
        count = User.objects.count()
        return render(request, 'core/users.html', {
            'users' : users,
            'count' : count
            })
    raise Http404()

@login_required
def writer(request, pk):
    admin = User.objects.get(email='tuenylukejoseph@gmail.com')
    if request.user == admin:
        bloger = User.objects.get(pk=pk)
        if bloger.profile.is_writer:
            bloger.profile.is_writer = False
            bloger.profile.save()
            value = 'Activate is_writer'
            writer = 'Not writer'
        else:
            bloger.profile.is_writer = True
            bloger.profile.save()
            value = 'De-activate is_writer'
            writer = 'writer'
        data = {}
        data['value'] = value
        data['writer'] = writer
        return JsonResponse(data)
    raise Http404()

@login_required
def delete_confirm_blog(request, pk):
    title = get_object_or_404(Titles, pk=pk)
    if title.user == request.user:
        message = title.title
        return render(request, 'core/delete_confirm.html', {
            'pk' : pk,
            'message' : message
            })
    raise Http404()

@login_required
def delete_blog(request, pk):
    title = get_object_or_404(Titles, pk=pk)
    if title.user == request.user:
        title.delete()
        return redirect('core:myblogs')
    raise Http404()

@login_required
def my_blog_display(request, args):
    title = get_object_or_404(Titles, pk=args)
    if title.user.email == request.user.email:
        data = Blog.objects.filter(title=title).last()
        comments = Comments.objects.filter(title=title).order_by('-datetime')
        raw_form = forms.CommentsForm()
        data_tiny = Blog.objects.filter(title=title).last()
        return render(request, 'core/display.html', {
            'data' : data,
            'title' : title,
            'content' : data_tiny,
            'raw_form' : raw_form,
            'comments' : comments
            })
    raise Http404()

@login_required
def update_crop_propic(request):
    user = request.user
    form = forms.ImageCropForm()
    if request.method == "POST":
        form = forms.ImageCropForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
#            if not user.profile.image == 'profile/img.png':
#                user.profile.image.delete()
            form.save()
        return redirect('core:profile', request.user.slug)
    return render(request, 'core/crop_image.html', {'form' : form})

@login_required
def allblogs(request):
    if request.user.email == 'tuenylukejoseph@gmail.com':
        blogs = Titles.objects.all()
        return render(request, 'core/allblogs.html', {'blogs' : blogs})
    else:
        raise Http404()

def m_profile(request, args):
    years = []
    years_months ={}
    profile = get_object_or_404(User, slug=args)
    blogs = Titles.objects.filter(is_published=True).filter(is_approved=True).filter(user=profile).order_by('-time_published')
    years_all = [i.year for i in blogs.values_list('time_published', flat=True)]
    dic = ['January', 'February', 'March' , 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    for y in years_all:
        if not y in years:
            years.append(y)
    for y in years:
        year_list_all = blogs.dates('time_published', 'year')
        year_list = year_list_all.filter(time_published__year = y)
        months = []
        months_all = [i.month for i in year_list.values_list('time_published', flat=True)]
        for m in months_all:
            if not dic[m-1] in months:
               months.append(dic[m-1])
        years_months[y] = months
    return render(request, 'core/m_profile.html', {
        'blogs' : blogs,
        'profile' : profile,
        'years_months' : years_months,
        })

def contact_view(request):
    form = forms.ContactForm()
    if request.method == 'POST':
        form = forms.ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['email']
            cc_myself = form.cleaned_data['cc_myself']

            recipients = ['josephtueny@gmail.com']
            if cc_myself:
                recipients.append(sender)
            if subject and message and sender:
                try:
                   send_mail(subject, message, sender, recipients)
                except BadHeaderError:
                    return render(request, 'core/contact.html', {'form' : form})
                return redirect('core:home')
            else:
                return render(request, 'core/contact.html', {'form' : form})
    return render(request, 'core/contact.html', {'form' : form})

def privacy_policy(request):
    return render(request, 'core/privacy_policy.html')

def about_us(request):
    writers = User.objects.filter(profile__is_writer = True)
    return render(request, 'core/about_us.html', {'writers' : writers})

def month_archieve(request, slug, year, month):
    dic = {'January' : 1, 'February' : 2, 'March' : 3 , 'April' : 4, 'May' : 5, 'June' : 6, 'July' : 7, 'August' : 8, 'September' : 9, 'October' : 10, 'November' : 11, 'December' : 12}
    month_index = dic[month]
    profile = get_object_or_404(User, slug=slug)
    blogs_year = Titles.objects.filter(is_published=True).filter(is_approved=True).filter(user=profile).order_by('-time_published').dates('time_published', 'year')
    blogs = Titles.objects.filter(is_published=True).filter(is_approved=True).filter(user=profile).order_by('-time_published').filter(time_published__year=year).filter(time_published__month=month_index)
    return render(request, 'core/month_archieve.html', {
        'blogs' : blogs,
        'slug' : slug,
        'year' : year,
        'month' : month,
        })

@login_required
def create_topic(request, args):
    admin = User.objects.get(email='tuenylukejoseph@gmail.com')
    if request.user == admin:
        form = forms.TopicForm()
        if request.method == 'POST':
            form = forms.TopicForm(request.POST)
            if form.is_valid:
                form = form.save(commit=False)
                max_length = Topic._meta.get_field('slug').max_length
                form.slug = orig = slugify(form.topic)[:max_length]
                for x in itertools.count(1):
                    if not Topic.objects.filter(slug=form.slug).exists():
                        break
                    form.slug = "%s-%d" % (orig[:max_length-len(str(x))-1], x)
                form.save()
                args = admin.slug
                return redirect('core:profile', args)
        return render(request, 'core/create_topic.html', {
            'form' : form,
            'args' : args
            })
    raise Http404()

def all_writers(request):
    writers = User.objects.filter(profile__is_writer=True)
    return render(request, 'core/all_writers.html', {
        'writers' : writers
        })

def topic_home(request, args):
    topic = get_object_or_404(Topic, slug=args)
    topics = Topic.objects.all()
    blogs = Titles.objects.filter(area=topic)
    return render(request, 'core/topic_home.html', {
        'blogs' : blogs,
        'topics' : topics,
        'topic' : topic
        })

def authenticate_user(request, args):
    email = request.POST.get('email', None)
    password = request.POST.get('password', None)
    user = auth_views_authenticate(request, email=email, password=password)
    if user is not None:
        login(request, user)
        title = get_object_or_404(Titles, slug=args)
        slug = title.user.slug
        return HttpResponse(json.dumps({'slug' : slug , 'args' : args, 'success' : 'yes'}))
    else:
        html_form = render_to_string('core/login_error.html', request=request)
        return JsonResponse({'html_form' : html_form, 'success' : 'no'})

def authenticate_display(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return HttpResponse(json.dumps({'success' : "yes"}))
        html_form = render_to_string('core/login_error_display.html', request=request)
        return JsonResponse({'html_form' : html_form, 'success' : 'no'})
    else:
        form = AuthenticationForm()
        context = {'form' : form}
        html_form = render_to_string('core/login_hidden.html', context, request=request)
        return JsonResponse({'html_form' : html_form, 'status' : 'done'})

@login_required
@user_passes_test(is_writer)
def blog_post(request, args):
    title = get_object_or_404(Titles, pk=args)
    title.is_published = False
    title.save()
    content = Blog.objects.filter(title=title).last()
    user = title.user
    if request.user == user:
        form = forms.BlogForm(instance=content)
        form2 = forms.BlogpicForm()
        form3 = forms.TitlesCoverForm()
        pk = args
        if request.method == 'POST':
            formblog = forms.BlogForm(request.POST, instance=content)
            if formblog.is_valid():
                formblog.save()
                return JsonResponse({})
            #    return HttpResponseRedirect(reverse('bookings:createblogs'))
        return render(request, 'core/blog-tinymce.html', {
            'form' : form,
            'form2' : form2,
            'form3' : form3,
            'pk'  : pk
            })
    raise Http404()

@login_required
@user_passes_test(is_writer)
def add_blog_pictures(request):
    pictureform = forms.BlogpicForm(request.POST, request.FILES)
    if pictureform.is_valid():
        image = pictureform.save(commit=False)
        pk = request.POST.get('pk', None)
        title = get_object_or_404(Titles, pk=pk)
        blog = Blog.objects.filter(title=title).last()
        image.blog = blog
        image.save()
#        pic_1 = request.POST.get('blobInfo', None)
#        pic = pic_1.file
#        pic_post = Blogpic(picture=pic)
#        pic_post.save()
        location = image.picture.url
        return JsonResponse({'location' : location})
    else:
        data = {}
        return JsonResponse(data)

@login_required
@user_passes_test(is_writer)
def add_description_theme(request, args):
    title = get_object_or_404(Titles, pk=args)
    user = title.user
    if request.user==user:
        try:
            content = title.titlesprop
            form = forms.TitlespropForm(instance=content)
        except ObjectDoesNotExist:
            form = forms.TitlespropForm()
        if request.method=='POST':
            try:
                content = title.titlesprop
                form = forms.TitlespropForm(request.POST, instance=content)
            except ObjectDoesNotExist:
                form = forms.TitlespropForm(request.POST)
            if form.is_valid():
                created_form = form.save(commit=False)
                created_form.title = title
                created_form.save()
                return redirect('core:blogpost', args)
        return render(request, 'core/description_theme.html', {
            'form' : form,
            'title' : title
            })
    raise Http404()

@login_required
def Create_Links(request):
    form = forms.UrlForm()
    args = request.user.slug
    if request.method == 'POST':
        formurl = forms.UrlForm(request.POST)
        if formurl.is_valid():
            created_form = formurl.save(commit=False)
            created_form.user = request.user
            created_form.save()
            return redirect('core:profile', args)
    return render(request, 'core/add_url.html', {
        'form': form
        })

@login_required
def edit_link(request, args):
    link = get_object_or_404(Url, pk=args)
    slug = request.user.slug
    if link.user == request.user:
        form = forms.UrlForm(instance=link)
        if request.method == 'POST':
            form = forms.UrlForm(request.POST, instance=link)
            if form.is_valid():
                form.save()
                return redirect('core:profile', slug)
        return render(request, 'core/add_url.html', {
            'form' : form,
            })
    raise Http404()

@login_required
def delete_link(request, args):
    link = get_object_or_404(Url, pk=args)
    slug = request.user.slug
    if link.user == request.user:
        link.delete()
        return redirect('core:profile', slug)
    raise Http404()

@login_required
@user_passes_test(is_writer)
def create_customtopic(request):
    form = forms.CustomTopicForm()
    if request.method == 'POST':
        formtop = forms.CustomTopicForm(request.POST)
        if formtop.is_valid():
            created_form = formtop.save(commit=False)
            created_form.user = request.user
            created_form.save()
            return redirect('core:customtopics')
    return render(request, 'core/add_customtopic.html', {
        'form' : form
        })

@login_required
@user_passes_test(is_writer)
def my_customtopics(request):
    topics = Customtopic.objects.filter(user=request.user)
    return render(request, 'core/customtopics.html', {
        'topics' : topics
        })

@login_required
@user_passes_test(is_writer)
def customtopic(request, args):
    topic = get_object_or_404(Customtopic, pk=args)
    user = topic.user
    if request.user == user:
        titles = topic.titles_set.all()
        titlesall = Titles.objects.filter(user=request.user).filter(customtopic=None)
        return render(request, 'core/customtopic.html', {
            'titles' : titles,
            'titlesall' : titlesall,
            'topic' : topic
            })
    raise Http404()

@login_required
@user_passes_test(is_writer)
def add_titles_to_customtopic(request, title, topic):
    title = get_object_or_404(Titles, pk=title)
    user = title.user
    if request.user == user:
        top = get_object_or_404(Customtopic, pk=topic)
        title.customtopic = top
        title.save()
        context = {'title' : title, 'topic' : topic }
        html_form = render_to_string('core/add_title.html', context, request=request)
        return JsonResponse({
            'html_form' : html_form
            })
    raise Http404()

@login_required
@user_passes_test(is_writer)
def remove_titles_from_customtopic(request, title, topic):
    title = get_object_or_404(Titles, pk=title)
    user = title.user
    if request.user == user:
        title.customtopic = None
        title.save()
        context = {'title' : title, 'topic' : topic }
        html_form = render_to_string('core/remove_title.html', context, request=request)
        return JsonResponse({
            'html_form' : html_form
            })
    raise Http404()

def profile_more(request, args):
    user = get_object_or_404(User, slug=args)
    topics_set = user.customtopic_set.all()
    topics = []
    for topic in topics_set:
        published = False
        for title in topic.titles_set.all():
            if title.is_published:
                published = True
                break
        if topic.titles_set.all() and published:
            topics.append(topic)
    return render(request, 'core/profile_more.html', {
        'topics' : topics,
        'profile' : user,
        })

def customtopic_blogs(request,args):
    topic = get_object_or_404(Customtopic, pk=args)
    subtopics = {}
    user = topic.user
    titles = topic.titles_set.filter(is_published=True).filter(is_approved=True).order_by('-time_published')
    count = topic.titles_set.filter(is_published=False).filter(is_approved=True).count()
    if request.user == user and topic.subtopic == None:
        subtopics = topic.topic.subtopic_set.all()
    return render(request, 'core/customtopic_blogs.html', {
        'titles' : titles,
        'profile' : user,
        'topic' : topic,
        'count' : count,
        'subtopics' : subtopics
        })

def search_blogs(request):
    title = request.GET.get('search-box', None)
    queryset = search(title)
    results = []
    for x in queryset:
        blog = Titles.objects.get(title=x.title)
        if blog.is_published and blog.is_approved:
            results.append(blog)
#    page = request.GET.get('page', 1)
#    paginator = Paginator(results, 3)
#    try:
#        results = paginator.page(page)
#    except PageNotAnInteger:
#        results = paginator.page(1)
#    except EmptyPage:
#        results = paginator.page(paginator.num_pages)
#    context = {'results' : results, 'title' : title}
#    html_form = render_to_string('core/search_blogs.html', context, request=request)
#    return JsonResponse({
#            'html_form' : html_form
#            })
    return render(request, 'core/search_blogs1.html', {'results' : results, 'title' : title})


def terms_conditions(request):
    return render(request, 'core/terms_conditions.html')

@login_required
@user_passes_test(is_writer)
def approval_blogs(request):
    if request.user.email == 'tuenylukejoseph@gmail.com':
        blogs = Titles.objects.filter(is_approved=False).filter(is_published=True)
        return render(request, 'core/approval_blogs.html', {'blogs' : blogs})
    raise Http404()

@login_required
def approval_display(request, args):
    title = get_object_or_404(Titles, pk=args)
    if request.user.email == 'tuenylukejoseph@gmail.com':
        data = Blog.objects.filter(title=title).last()
        comments = Comments.objects.filter(title=title).order_by('-datetime')
        raw_form = forms.CommentsForm()
        data_tiny = Blog.objects.filter(title=title).last()
        return render(request, 'core/display.html', {
            'data' : data,
            'title' : title,
            'content' : data_tiny,
            'raw_form' : raw_form,
            'comments' : comments
            })
    raise Http404()

@login_required
def approve(request, args):
    title = get_object_or_404(Titles, pk=args)
    if request.user.email == 'tuenylukejoseph@gmail.com':
        title.is_approved = True
        title.save()
        return redirect('core:approval_blogs')
    raise Http404()

@login_required
@user_passes_test(is_writer)
def update_usercover(request):
    user = request.user
    form = forms.UsercoverForm()
    if request.method == "POST":
        form = forms.UsercoverForm(request.POST, request.FILES)
        if form.is_valid():
            s = user.usercover_set.all()
            if s is not None:
                for i in s:
                    i.delete()
            created_cover = form.save(commit=False)
            created_cover.user = user
            created_cover.save()
            return redirect('core:user_theme')
    return render(request, 'core/usercover.html', {'form' : form})

@login_required
@user_passes_test(is_writer)
def add_usercover_theme(request):
    user = request.user
    try:
        content = user.usertheme
        form = forms.UserthemeForm(instance=content)
    except ObjectDoesNotExist:
        form = forms.UserthemeForm()
    if request.method=='POST':
        try:
            content = user.usertheme
            form = forms.UserthemeForm(request.POST, instance=content)
        except ObjectDoesNotExist:
            form = forms.UserthemeForm(request.POST)
        if form.is_valid():
            created_form = form.save(commit=False)
            created_form.user = user
            created_form.save()
            return redirect('core:profile', request.user.slug)
    return render(request, 'core/usertheme.html', {
        'form' : form,
        'user' : user
        })

@login_required
@user_passes_test(is_writer)
def add_quote(request):
    user = request.user
    try:
        content = user.usertheme
        form = forms.UserquoteForm(instance=content)
    except ObjectDoesNotExist:
        form = forms.UserquoteForm()
    if request.method=='POST':
        try:
            content = user.usertheme
            form = forms.UserquoteForm(request.POST, instance=content)
        except ObjectDoesNotExist:
            form = forms.UserquoteForm(request.POST)
        if form.is_valid():
            created_form = form.save(commit=False)
            created_form.user = user
            created_form.save()
            return redirect('core:user_theme')
    return render(request, 'core/userquote.html', {
        'form' : form,
        })

def create_manual_titlesprop(request):
    user = request.user
    if user.email == 'tuenylukejoseph@gmail.com':
        titles = Titles.objects.filter(titlesprop=None)
        for t in titles:
            titlesprop = Titlesprop.objects.create()
            t.titlesprop = titlesprop
            t.save()
        return redirect('core:profile', user.slug)
    raise Http404()

def alltopics(request):
    topics_set = Topic.objects.all()
    topics = []
    for topic in topics_set:
        published = False
        for title in topic.titles_set.all():
            if title.is_published:
                published = True
                break
        if topic.titles_set.all() and published:
            topics.append(topic)
    return render(request, 'core/alltopics.html', {
        'topics' : topics
        })

def topic_titles(request, args):
#    profile = User.objects.get(email='joseph@gmail.com')
    topic = Topic.objects.get(slug=args)
    blogs_list = topic.titles_set.filter(is_published=True).filter(is_approved=True).order_by('-time_published')
    page = request.GET.get('page',1)
    paginator = Paginator(blogs_list, 5)
    try:
        blogs = paginator.page(page)
    except PageNotAnInteger:
        blogs = paginator.page(1)
    except EmptyPage:
        blogs = paginator.page(paginator.num_pages)

    topics = Topic.objects.all()
    return render(request, 'core/home_topic.html', {
        'blogdata' : blogs,
        'topic' : topic
        })

@login_required
def create_subtopic(request, args):
    admin = User.objects.get(email='tuenylukejoseph@gmail.com')
    if request.user == admin:
        form = forms.SubtopicForm()
        if request.method == 'POST':
            form = forms.SubtopicForm(request.POST)
            if form.is_valid():
                form = form.save(commit=False)
                max_length = Subtopic._meta.get_field('slug').max_length
                form.slug = orig = slugify(form.subtopic)[:max_length]
                for x in itertools.count(1):
                    if not Subtopic.objects.filter(slug=form.slug).exists():
                        break
                    form.slug = "%s-%d" % (orig[:max_length-len(str(x))-1], x)
                form.save()
                args = admin.slug
                return redirect('core:profile', args)
        return render(request, 'core/create_topic.html', {
            'form' : form,
            'args' : args
            })
    raise Http404()

@login_required
@user_passes_test(is_writer)
def add_to_subtopic(request, pk):
    topic = get_object_or_404(Customtopic, pk=pk)
    slug = request.POST.get('slug', None)
    subtopic = get_object_or_404(Subtopic, slug=slug)
    topic.subtopic = subtopic
    topic.save()
    return JsonResponse({})

def topic_more(request, args):
    topic = get_object_or_404(Topic, slug=args)
    topics_set = topic.subtopic_set.all()
    topics = []
    for topic in topics_set:
        for custom in topic.customtopic_set.all():
            published = False
            for title in custom.titles_set.all():
                if title.is_published:
                    published = True
                    break
            if custom.titles_set.all() and published:
                topics.append(topic)
                break
    return render(request, 'core/topic_more.html', {
        'topics' : topics,
        'args' : args,
        'topic' : topic.topic
        })

def subtopic_blogs(request, args):
    topic = Subtopic.objects.get(slug=args)
    topics = topic.customtopic_set.all()
    top = topic.topic
    return render(request, 'core/allsubtopics.html', {
        'topics' : topics,
        'topic' : topic,
        'top' : top
        })

def subtopic_customtopic_blogs(request,args):
    topic = get_object_or_404(Customtopic, pk=args)
    subtopic = topic.subtopic
    titles = topic.titles_set.filter(is_published=True).filter(is_approved=True)
    return render(request, 'core/subtopic_customtopic_blogs.html', {
        'titles' : titles,
        'topic' : topic,
        'subtopic' : subtopic
        })

#def pininterest(request):
#    return render(request, 'core/pinterest-7a703.html')

