from django.contrib.auth import get_user_model
from django.forms import ModelForm

from .models import Post

User = get_user_model()


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group']
        labels = {
            'group': 'Группа',
            'text': 'Текст',
        }
