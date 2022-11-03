from posts.forms import PostForm
from posts.models import Group, Post
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


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
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        """Валидная форма создаёт запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый новый пост',
            'group': PostCreateFormTests.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', args=[PostCreateFormTests.user]))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(text=form_data['text']).exists()
        )

    def test_post_edit(self):
        """Валидная форма редактирует запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый отредактированый пост',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}))
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(
            Post.objects.filter(text=form_data['text']).exists()
        )
