from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.utils import timezone, six
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from .manager import UserManager
from PIL import Image as Img
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
from tinymce.models import HTMLField



# Create your models here.

def user_directory_path(instance, filename):
    return 'images/user_{0}/{1}'.format(instance.title.id, filename)

def user_picset_path(instance, filename):
    return 'picset/user_{0}/{1}'.format(instance.picsettitle.id, filename)

def user_blogpic_path(instance, filename):
    return 'blogpic/title_{0}/{1}'.format(instance.blog.title.id, filename)
class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(max_length=15, unique=True, blank=True, null=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    slug = models.SlugField(blank=True, default='')
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. unselect this instad of deleting accounts.')
    )

    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    location = models.CharField(max_length=30, blank=True, default='')
    image = models.ImageField(upload_to='profile', default='profile/img.png')
    bio = models.TextField(max_length=800, blank=True, default='')
    email_confirmed = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    is_writer = models.BooleanField(default=False)

class Usercover(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    cover = models.ImageField(upload_to='cover/', verbose_name='cover', blank=True)

    def save(self, *args, **kwargs):
        if self.cover:
            img = Img.open(BytesIO(self.cover.read()))
            img.thumbnail((self.cover.width, self.cover.height), Img.ANTIALIAS)
            output = BytesIO()
            img.save(output, format='JPEG', quality=20)
            output.seek(0)
            self.cover = InMemoryUploadedFile(output, 'ImageField', "%s.jpg" %self.cover.name.split('.')[0], 'image/jpeg', output.tell(), None)
        return super(Usercover, self).save(*args, **kwargs)

class Usertheme(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    quote = models.CharField(max_length=100, blank=True, default='')
    description_font = models.CharField(max_length=100, blank=True, null=True, default='Times, serif')
    description_color = models.CharField(max_length=50, blank=True, null=True, default='black')


class Url(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    url_name = models.CharField(max_length=20)
    url = models.URLField()

class Topic(models.Model):
    topic = models.CharField(max_length=15, unique=True)
    slug = models.SlugField(blank=True, default='')

    def __str__(self):
        return self.topic

class Subtopic(models.Model):
    subtopic = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    slug = models.SlugField(blank=True, default='')

    def __str__(self):
        return self.subtopic

class Customtopic(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, blank=True, null=True)
    subtopic = models.ForeignKey(Subtopic, on_delete=models.CASCADE, blank=True, null=True)

class Titles(models.Model):
    title = models.CharField(max_length=80)
#    topic = models.CharField(max_length=20, blank=True)
    area = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True)
    cover = models.ImageField(upload_to='title/', verbose_name='cover', blank=True)
    description = models.CharField(max_length=325, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    time_published = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(default = timezone.now)
    is_published = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    slug = models.SlugField(default='')
    authenticated_views = models.IntegerField(blank=True, default=0)
    total_views = models.IntegerField(blank=True, default=0)
    last_order = models.IntegerField(default=0)
    customtopic = models.ForeignKey(Customtopic, on_delete=models.CASCADE, blank=True, null=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def first_image(self):
        if self.coverpic_set.all():
            return self.coverpic_set.all()[0]
        return None

class Coverpic(models.Model):
    title = models.ForeignKey(Titles, on_delete=models.CASCADE, blank=True, null=True)
    cover = models.ImageField(upload_to='title/', verbose_name='cover', blank=True)

    def save(self, *args, **kwargs):
        if self.cover:
            img = Img.open(BytesIO(self.cover.read()))
            img.thumbnail((self.cover.width, self.cover.height), Img.ANTIALIAS)
            output = BytesIO()
            img.save(output, format='JPEG', quality=20)
            output.seek(0)
            self.cover = InMemoryUploadedFile(output, 'ImageField', "%s.jpg" %self.cover.name.split('.')[0], 'image/jpeg', output.tell(), None)
        return super(Coverpic, self).save(*args, **kwargs)

class Comments(models.Model):
    title = models.ForeignKey(Titles, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reply = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    comment = models.TextField()
    datetime = models.DateTimeField(auto_now_add=True)

class Default_Pic(models.Model):
    image = models.ImageField(upload_to='profile')

class Titlesprop(models.Model):
    title = models.OneToOneField(Titles, on_delete=models.CASCADE, blank=True, null=True)
    title_font = models.CharField(max_length=100, blank=True, null=True, default='Times, serif')
    description_font = models.CharField(max_length=100, blank=True, null=True, default='Times, serif')
    title_color = models.CharField(max_length=50, blank=True, null=True, default='black')
    description_color = models.CharField(max_length=50, blank=True, null=True, default='black')
    cover_color = models.CharField(max_length=50, blank=True, null=True, default='#DCDCDC')


class Blog(models.Model):
    title = models.OneToOneField(Titles, on_delete=models.CASCADE)
    content = HTMLField('Content')

class Blogpic(models.Model):
    picture = models.ImageField(upload_to=user_blogpic_path, verbose_name='picture')
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.picture:
            img = Img.open(BytesIO(self.picture.read()))
            img.thumbnail((self.picture.width, self.picture.height), Img.ANTIALIAS)
            output = BytesIO()
            if img.mode in ("RGBA", "P"):
               img = img.convert("RGB")
            img.save(output, format='JPEG', quality=20)
            output.seek(0)
            self.picture = InMemoryUploadedFile(output, 'ImageField', "%s.jpg" %self.picture.name.split('.')[0], 'image/jpeg', output.tell(), None)
        return super(Blogpic, self).save(*args, **kwargs)

