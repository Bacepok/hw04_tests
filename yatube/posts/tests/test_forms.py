from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='тестовое описание группы'
        )

        cls.post = Post.objects.create(
            text='тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        """Валидная форма создаёт запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый новый пост',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        last_post = Post.objects.first()
        self.assertRedirects(response, reverse(
            'posts:profile', args=[self.user]))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(last_post.group, self.group)
        self.assertEqual(last_post.author, self.user)

    def test_post_edit(self):
        """Валидная форма редактирует запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            'id': self.post.pk,
            'text': 'Тестовый отредактированый пост',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        last_post = Post.objects.get(id=self.post.pk)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}))
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(last_post.group, self.group)
        self.assertEqual(last_post.author, self.user)

    def test_redirect_guest_client(self):
        """Неавторизованный пользователь не может редактировать пост"""
        form_data = {
            'text': 'Тестовый новый пост',
            'group': self.group.id
        }
        response = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            (reverse('users:login')
             + '?next='
             + reverse('posts:post_edit', kwargs={'post_id': self.post.pk})),
        )
