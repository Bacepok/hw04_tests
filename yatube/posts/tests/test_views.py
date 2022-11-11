from django.conf import settings
from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()
POST_COUTN_FOR_TEST: int = 27


class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='тестовое описание группы'
        )
        cls.URL_INDEX = reverse('posts:index')
        cls.URL_USER = reverse(
            'posts:profile', kwargs={'username': cls.user.username})
        cls.URL_GROUP = reverse(
            'posts:group_list', kwargs={'slug': cls.group.slug})
        cls.URL_CREATE = reverse('posts:post_create')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post = Post.objects.create(
            text='тестовый текст',
            author=cls.user,
            group=cls.group,
        )
        cls.URL_POST = reverse(
            'posts:post_detail', kwargs={'post_id': cls.post.id})
        cls.URL_POST_EDIT = reverse(
            'posts:post_edit', kwargs={'post_id': cls.post.id})

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = [
            ('posts/index.html', self.URL_INDEX),
            ('posts/group_list.html', self.URL_GROUP),
            ('posts/profile.html', self.URL_USER),
            ('posts/post_detail.html', self.URL_POST),
            ('posts/create_post.html', self.URL_CREATE),
            ('posts/create_post.html', self.URL_POST_EDIT),
        ]

        for template, reverse_name in templates_page_names:
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.URL_INDEX)
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.group, self.post.group)
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.author, self.post.author)
        self.assertEqual(first_object.id, self.post.id)

    def test_post_added_correctly(self):
        """Пост при создании добавлен корректно"""
        response_index = self.authorized_client.get(self.URL_INDEX)
        response_group = self.authorized_client.get(self.URL_GROUP)
        response_profile = self.authorized_client.get(self.URL_USER)
        index = response_index.context['page_obj']
        group = response_group.context['page_obj']
        profile = response_profile.context['page_obj']
        self.assertIn(self.post, index, 'поста нет на главной')
        self.assertIn(self.post, group, 'поста нет в профиле')
        self.assertIn(self.post, profile, 'поста нет в группе')

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.URL_POST)
        context_post = response.context['post']
        post_text = {context_post.text: self.post.text,
                     context_post.group: self.group,
                     context_post.author: self.user.username}
        for value, expected in post_text.items():
            self.assertEqual(post_text[value], expected)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.URL_CREATE)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='тестовое описание группы'
        )
        cls.guest_client = Client()
        cls.posts = Post.objects.bulk_create(
            [
                Post(
                    text='тестовый текст ' + str(i),
                    author=cls.user,
                    group=cls.group,
                )
                for i in range(POST_COUTN_FOR_TEST)
            ]
        )
        cls.URL_INDEX = reverse('posts:index')
        cls.URL_USER = reverse(
            'posts:profile', kwargs={'username': cls.user.username})
        cls.URL_GROUP = reverse(
            'posts:group_list', kwargs={'slug': cls.group.slug})

    def test_correct_page_paginator(self):
        '''Проверка количества постов на первой и последней страницах. '''
        pages_rest = POST_COUTN_FOR_TEST % settings.POSTS_IN_PAGE
        pages = (self.URL_INDEX,
                 self.URL_USER,
                 self.URL_GROUP)
        for page in pages:
            response1 = self.guest_client.get(page)
            response2 = self.guest_client.get(page + f'?page={pages_rest}')
            count_posts1 = len(response1.context['page_obj'])
            count_posts2 = len(response2.context['page_obj'])
            error_name1 = (f'Ошибка: {count_posts1} постов,'
                           f' должно {settings.POSTS_IN_PAGE}')
            error_name2 = (f'Ошибка: {count_posts2} постов,'
                           f'должно {pages_rest}')
            self.assertEqual(count_posts1, settings.POSTS_IN_PAGE, error_name1)
            self.assertEqual(count_posts2, pages_rest, error_name2)
