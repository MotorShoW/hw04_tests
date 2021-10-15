from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostsPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Name')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.posts = Post.objects.create(
            author=cls.user,
            text='Тест текст',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = PostsPagesTest.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """Проверка использования URL соответствующего шаблона"""
        template_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}): (
                'posts/group_list.html'),
            reverse('posts:profile', kwargs={'username': self.user}): (
                'posts/profile.html'),
            reverse('posts:post_detail', kwargs={'post_id': 1}): (
                'posts/post_detail.html'),
            reverse('posts:post_edit', kwargs={'post_id': 1}): (
                'posts/create_post.html'),
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in template_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом"""
        response = self.guest_client.get(reverse('posts:index'))
        first_object = response.context.get('page_obj').object_list[0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_author_0 = first_object.author.username
        self.assertEqual(post_text_0, 'Тест текст')
        self.assertEqual(post_group_0, self.group.title)
        self.assertEqual(post_author_0, self.user.username)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом"""
        response = self.guest_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'test-slug'}))
        first_object = response.context.get('page_obj').object_list[0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_author_0 = first_object.author.username
        self.assertEqual(post_text_0, 'Тест текст')
        self.assertEqual(post_group_0, self.group.title)
        self.assertEqual(post_author_0, self.user.username)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.guest_client.get(reverse(
            'posts:profile', kwargs={'username': self.user}))
        first_object = response.context.get('page_obj').object_list[0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_author_0 = first_object.author.username
        self.assertEqual(post_text_0, 'Тест текст')
        self.assertEqual(post_group_0, self.group.title)
        self.assertEqual(post_author_0, self.user.username)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом"""
        response = self.guest_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': 1}))
        first_object = response.context.get('post')
        post_text = first_object.text
        post_group = first_object.group.title
        post_author = first_object.author.username
        self.assertEqual(post_text, 'Тест текст')
        self.assertEqual(post_group, self.group.title)
        self.assertEqual(post_author, self.user.username)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': 1}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_shows_on_index_page(self):
        """Пост появился на главной странице"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertContains(response, self.posts.text)

    def test_post_shows_on_group_page(self):
        """Пост появился на странице группы"""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'test-slug'}))
        self.assertContains(response, self.posts.text)

    def test_post_shows_on_profile_page(self):
        """Пост появился на странице профиля"""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'Name'}))
        self.assertContains(response, self.posts.text)

    def test_post_not_in_other_group_page(self):
        """Пост НЕ появился на странице чужой группы"""
        Group.objects.create(
            title='Клуб любителей пощекотать свое...',
            slug='Anime-Club',
            description='Дон Педрильо',
        )
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'Anime-Club'}))
        self.assertNotContains(response, self.posts.text)


class PaginatorViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Name')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.posts = [
            Post.objects.create(
                author=cls.user,
                text='Тест текст' + str(i),
                group=cls.group,
            )
            for i in range(15)
        ]

    def setUp(self):
        self.guest_client = Client()
        self.user = PaginatorViewTest.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_page_contains_ten_records(self):
        first_page = 10
        second_page = 5
        context = {
            reverse('posts:index'): first_page,
            reverse('posts:index') + '?page=2': second_page,
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
            first_page,
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
            + '?page=2': second_page,
            reverse('posts:profile', kwargs={'username': self.user}):
            first_page,
            reverse('posts:profile', kwargs={'username': self.user})
            + '?page=2': second_page,
        }
        for reverse_page, len_count in context.items():
            with self.subTest(reverse=reverse):
                self.assertEqual(len(self.client.get(
                    reverse_page).context.get('page_obj')), len_count)
