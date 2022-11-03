from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.user = User.objects.create_user(username='auth')
        self.group = Group.objects.create(title='Тестовая группа',
                                          slug='Тестовый слаг',
                                          description='Тестовое описание',)
        self.post = Post.objects.create(author=self.user,
                                        text='Тестовое описание поста' * 5,)

    def test_models_have_correct_object_names(self):
        '''Проверка длины __str__ post'''
        error_name = f"Вывод не имеет {settings.LEN_OF_POSTS} символов"
        self.assertEqual(self.post.__str__(),
                         self.post.text[:settings.LEN_OF_POSTS],
                         error_name)

    def test_models_have_correct_group_title(self):
        '''Проверка title группы'''
        error_name = f"Вывод не соответствует {self.group.title}"
        self.assertEqual(self.group.__str__(),
                         self.group.title,
                         error_name)

    def test_title_label(self):
        '''Проверка заполнения verbose_name'''
        field_verboses = {'text': 'Текст публикации',
                          'pub_date': 'Дата публикации',
                          'group': 'Группа',
                          'author': 'Автор'}
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                error_name = f'Поле {field} ожидало значение {expected_value}'
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value, error_name)
