from .models import Profile, User, Titles, Blog, Titlesprop
from django.db.models.signals import post_save

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)

def create_titles_blog(sender, instance, created, **kwargs):
    if created:
        Blog.objects.create(title=instance)

def save_titles_blog(sender, instance, **kwargs):
    instance.blog.save()

post_save.connect(create_titles_blog, sender=Titles)
post_save.connect(save_titles_blog, sender=Titles)

def create_titlesprop(sender, instance, created, **kwargs):
    if created:
        Titlesprop.objects.create(title=instance)

def save_titlesprop(sender, instance, **kwargs):
    instance.titlesprop.save()

post_save.connect(create_titlesprop, sender=Titles)
post_save.connect(save_titlesprop, sender=Titles)