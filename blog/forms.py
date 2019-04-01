from django import forms
from .models import Post, Comment
from ckeditor.widgets import CKEditorWidget


class PostCreateForm(forms.ModelForm):

    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Post
        fields = (
            'title',
            'overview',
            'content',
            'status',
            'restrict_comments',
        )


# class UserLoginForm(forms.Form):
#     username = forms.CharField(label='Username')
#     password = forms.CharField(label='Password', widget=forms.PasswordInput)

class CommentForm(forms.ModelForm):
    text = forms.CharField(label="", 
        widget=forms.Textarea(attrs={'class': 'form-control',
                                'placeholder': 'Text Goes Here!',
                                'rows':'4', 'cols':'50'}))
    class Meta:
        model = Comment
        fields = ('text',)