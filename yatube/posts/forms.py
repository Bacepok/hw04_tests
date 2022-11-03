from django import forms
from django.utils.translation import gettext_lazy as ht

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        labels = {
            'text': ht('Текст публикации'),
        }
        help_texts = {
            'text': ht('Текст новой публикации'),
            'group': ht('Группа, к которой будет относиться публикация')
        }
