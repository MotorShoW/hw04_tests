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
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тест текст',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def assert_info(self, post, expected_post):
        """Проверка ожидаемого поста"""
        self.assertEqual(post.text, expected_post.text)
        self.assertEqual(post.group, expected_post.group)
        self.assertEqual(post.author, expected_post.author)

    def test_pages_uses_correct_template(self):
        """Проверка использования URL соответствующего шаблона"""
        template_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}): (
                'posts/group_list.html'),
            reverse('posts:profile', kwargs={'username': self.user}): (
                'posts/profile.html'),
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}): (
                'posts/post_detail.html'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}): (
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
        post = response.context['page_obj'][0]
        expected_post = self.post
        self.assert_info(post, expected_post)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом"""
        response = self.guest_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}))
        post = response.context['page_obj'][0]
        expected_post = self.post
        self.assert_info(post, expected_post)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.guest_client.get(reverse(
            'posts:profile', kwargs={'username': self.user}))
        post = response.context['page_obj'][0]
        expected_post = self.post
        self.assert_info(post, expected_post)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом"""
        response = self.guest_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        post = response.context['post']
        expected_post = self.post
        self.assert_info(post, expected_post)

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
            'posts:post_edit', kwargs={'post_id': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_shows_on_pages(self):
        """Пост появился на страницах index, group, profile"""
        new_post = Post.objects.create(
            author=self.user,
            text='Новый пост',
            group=self.group,
        )
        urls = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user}),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertContains(response, new_post)

    def test_post_not_in_other_group_page(self):
        """Пост НЕ появился на странице чужой группы"""
        new_post = Post.objects.create(
            author=self.user,
            text='Новый пост',
            group=self.group,
        )
        Group.objects.create(
            title='Клуб любителей пощекотать свое...',
            slug='Anime-Club',
            description='Дон Педрильо',
        )
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'Anime-Club'}))
        self.assertNotContains(response, new_post)


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
        Post.objects.bulk_create(
            Post(
                text=(f'Тест текст + {i}'),
                author=cls.user,
                group=cls.group
            )
            for i in range(15)
        )

    def setUp(self):
        self.guest_client = Client()
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
