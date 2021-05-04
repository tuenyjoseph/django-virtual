from django import forms
from .models import User, Profile
from . import models
from PIL import Image
from django.core.files import File
from django.core.files.storage import default_storage as storage
from django.contrib.auth.forms import AuthenticationForm
from tinymce.widgets import TinyMCE

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label = 'Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name',]

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class NameUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
    def save(self, commit=True):
        user = super(NameUpdateForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class LocationUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['location']
    def save(self, commit=True):
        profile = super(LocationUpdateForm, self).save(commit=False)
        profile.location = self.cleaned_data['location']
        if commit:
            profile.save()
        return profile

class BioUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio']
        widgets = {
           'bio' : forms.Textarea(attrs={'class' : 'form-control' , 'placeholder' : 'Max words - 800'})
        }
    def save(self, commit=True):
        profile = super(BioUpdateForm, self).save(commit=False)
        profile.bio = self.cleaned_data['bio']
        if commit:
            profile.save()
        return profile

class ImageUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']
    def save(self, commit=True):
        profile = super(ImageUpdateForm, self).save(commit=False)
        profile.image = self.cleaned_data['image']
        if commit:
            profile.save()
        return profile

class TitlesForm(forms.ModelForm):

    class Meta:
        model = models.Titles
        fields = ['title', 'area', 'description',]
        widgets = {
            'title' : forms.TextInput(attrs={'class' : 'form-control', 'placeholder' : 'Enter title of the blog here'}),
            'description' : forms.Textarea(attrs={'class' : 'form-control', 'placeholder' : 'Write a short description about the article you are writing'}),
        }


class TitlesCoverForm(forms.ModelForm):
    class Meta:
        model = models.Coverpic
        fields = ['cover']

class CommentsForm(forms.ModelForm):
    class Meta:
        model = models.Comments
        fields = ['comment']
        widgets = {
            'text' : forms.TextInput(
                attrs={'id':'post-text', 'required' :True,}
                ),
            'comment' : forms.Textarea(attrs={'class' : 'form-control'}),
        }


class ReplyForm(forms.ModelForm):
    class Meta:
        model = models.Comments
        fields = ['comment']
        widgets = {
            'text' : forms.TextInput(
                attrs={'id':'post-text', 'required' :True,}
                ),
            'comment' : forms.Textarea(attrs={'class' : 'form-control', 'id':'post-reply'}),
        }

class ImageCropForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = Profile
        fields = ('image', 'x', 'y', 'width', 'height',)
    def save(self):
        profile = super(ImageCropForm, self).save()

        x = self.cleaned_data.get('x')
        y = self.cleaned_data.get('y')
        w = self.cleaned_data.get('width')
        h = self.cleaned_data.get('height')

        image = Image.open(profile.image)
        cropped_image = image.crop((x, y, w+x, h+y))
        resized_image =cropped_image.resize((200, 200), Image.ANTIALIAS)
        fh = storage.open(profile.image.name, "wb")
        format = 'png'
        resized_image.save(fh, format)
        fh.close()
        return profile

class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class' : 'form-control'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class' : 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class' : 'form-control', 'placeholder' : 'Please leave your email address for us to get back'}))
    cc_myself = forms.BooleanField(required=False)

class TopicForm(forms.ModelForm):
    class Meta:
        model = models.Topic
        fields = ['topic']

class BlogForm(forms.ModelForm):
    content = forms.CharField(
        widget=TinyMCE(attrs={
            'required' : False,
            'cols' : 30,
            'rows' : 10,
            }))

    class Meta:
        model = models.Blog
        fields = ['content']

    def __init__(self, *args, **kwargs):
        super(BlogForm, self).__init__(*args, **kwargs)
        self.fields['content'].label = ''


class BlogpicForm(forms.ModelForm):
    class Meta:
        model = models.Blogpic
        fields = ['picture']

class TitlespropForm(forms.ModelForm):
    class Meta:
        model = models.Titlesprop
        fields = ['title_font', 'description_font', 'title_color', 'description_color', 'cover_color']


class UrlForm(forms.ModelForm):
    class Meta:
        model = models.Url
        fields = ['url_name', 'url']

        widgets = {
            'url_name' : forms.TextInput(
                attrs={'class' : 'form-control', 'required' :True,}
                ),
            'url' : forms.TextInput(
                attrs={'class' : 'form-control', 'required' :True,}
                ),
        }

class ResendActivationLinkForm(forms.Form):
    email = forms.EmailField(label=("email"))

class CustomTopicForm(forms.ModelForm):
    class Meta:
        model = models.Customtopic
        fields = ['name', 'description', 'topic']
        widgets = {
            'name' : forms.TextInput(attrs={'class' : 'form-control', 'placeholder' : 'Enter name of the set here'}),
            'description' : forms.Textarea(attrs={'class' : 'form-control', 'placeholder' : 'Write a short description about the set of blogs you are writing under this topic or set'}),
        }

class UsercoverForm(forms.ModelForm):
    class Meta:
        model = models.Usercover
        fields = ['cover']

class UserthemeForm(forms.ModelForm):
    class Meta:
        model = models.Usertheme
        fields = ['description_font', 'description_color']

class UserquoteForm(forms.ModelForm):
    class Meta:
        model = models.Usertheme
        fields = ['quote']
        widgets = {
            'quote' : forms.TextInput(attrs={'class' : 'form-control', 'placeholder' : 'Enter your quote'})
        }

class SubtopicForm(forms.ModelForm):
    class Meta:
        model = models.Subtopic
        fields = ['subtopic','description', 'topic']
        widgets = {
            'name' : forms.TextInput(attrs={'class' : 'form-control', 'placeholder' : 'Enter name of the subtopic'}),
            'description' : forms.Textarea(attrs={'class' : 'form-control', 'placeholder' : 'Write a short description about this subtopic'})
        }




