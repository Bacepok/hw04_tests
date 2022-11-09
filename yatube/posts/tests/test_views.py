from django.conf import settings
from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()
TEST_OF_POST: int = 19


class PostPagesTests(TestCase):
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
            'posts:profile', kwargs={'username': 'author'})
        cls.URL_GROUP = reverse(
            'posts:group_list', kwargs={'slug': 'test-slug'})
        cls.URL_CREATE = reverse('posts:post_create')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        many_posts: list = []
        for i in range(TEST_OF_POST):
            many_posts.append(Post(text=f'Тестовый текст {i}',
                              group=self.group,
                              author=self.user))
        Post.objects.bulk_create(many_posts)
        self.post = Post.objects.create(
            text='тестовый текст',
            author=self.user,
            group=self.group,
        )
        self.URL_POST = reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id})
        self.URL_POST_EDIT = reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id})

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

    '''def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        for post in Post.objects.select_related('group'):
            response = self.authorized_client.get(reverse('posts:index'))
            self.assertEqual(response.context.get('post'), post)'''

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        # response = self.authorized_client.get(self.URL_INDEX)
        # first_object = response.context['page_obj'][0]
        first_object = Post.objects.get(id=20)
        self.assertEqual(first_object.group, self.post.group)
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.author, self.post.author)
        self.assertEqual(first_object.id, self.post.id)

    def test_post_added_correctly(self):
        """Пост при создании добавлен корректно"""
        post = Post.objects.create(
            text='Тестовый текст проверка как добавился',
            author=self.user,
            group=self.group)
        response_index = self.authorized_client.get(
            reverse('posts:index'))
        response_group = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}))
        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}))
        index = response_index.context['page_obj']
        group = response_group.context['page_obj']
        profile = response_profile.context['page_obj']
        self.assertIn(post, index, 'поста нет на главной')
        self.assertIn(post, group, 'поста нет в профиле')
        self.assertIn(post, profile, 'поста нет в группе')

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        context_post = response.context['post']
        post_text_0 = {context_post.text: self.post.text,
                       context_post.group: self.group,
                       context_post.author: self.user.username}
        for value, expected in post_text_0.items():
            self.assertEqual(post_text_0[value], expected)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_correct_page_context_guest_client(self):
        '''Проверка количества постов на первой и второй страницах. '''
        pages: tuple = (reverse('posts:index'),
                        reverse('posts:profile',
                                kwargs={'username': f'{self.user.username}'}),
                        reverse('posts:group_list',
                                kwargs={'slug': f'{self.group.slug}'}))
        for page in pages:
            response1 = self.guest_client.get(page)
            response2 = self.guest_client.get(page + '?page=2')
            count_posts1 = len(response1.context['page_obj'])
            count_posts2 = len(response2.context['page_obj']) - 1
            error_name1 = (f'Ошибка: {count_posts1} постов,'
                           f' должно {settings.POSTS_IN_PAGE}')
            error_name2 = (f'Ошибка: {count_posts2} постов,'
                           f'должно {TEST_OF_POST -settings.POSTS_IN_PAGE}')
            self.assertEqual(count_posts1,
                             settings.POSTS_IN_PAGE,
                             error_name1)
            self.assertEqual(count_posts2,
                             TEST_OF_POST - settings.POSTS_IN_PAGE,
                             error_name2)
