# posts/tests/test_urls.py
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
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

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_url_exists_at_desired_location(self):
        """Страница группы доступна любому пользователю."""
        response = self.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_url_exists_at_desired_location(self):
        """Страница поста доступна любому пользователю."""
        error_name = f'Вывод не соответствует. Пост id {self.post.id}'
        response = self.guest_client.get(f'/posts/{self.post.id}/')
        self.assertEqual(response.status_code, HTTPStatus.OK, error_name)

    def test_author_url_exists_at_desired_location(self):
        """Страница автора доступна любому пользователю."""
        error_name = f'Вывод не соответствует. Автор - {self.user.username}'
        response = self.guest_client.get(f'/profile/{self.user.username}/')
        self.assertEqual(response.status_code, HTTPStatus.OK, error_name)

    def test_post_create_url_exists_at_desired_location_authorized(self):
        """Страница создания доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_exists_at_desired_location_authorized(self):
        """Страница редактирования доступна автору. """
        error_name = f'Вывод не соответствует - /posts/{self.post.id}/edit/'
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK, error_name)

    def test_unknown_page_url_unexists_at_desired_location(self):
        """404 страница возвращает 404"""
        response = Client().get('/404_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_create_url_redirect_anonymous_on_admin_login(self):
        """Страница /create/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/create_post.html': '/create/',
            'posts/group_list.html': '/group/test-slug/',
            'posts/profile.html': f'/profile/{self.user.username}/',
            'posts/post_detail.html': f'/posts/{self.post.id}/',
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

        for template, address in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
