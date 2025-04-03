from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    content = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'Write your comment here...'}))
    
    class Meta:
        model = Comment
        fields = ['content']
