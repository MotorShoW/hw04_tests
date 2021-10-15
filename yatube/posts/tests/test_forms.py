from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()


class PostsFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()
        cls.user = User.objects.create_user(username='Name')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тест текст',
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.user = PostsFormTest.user
        self.authorized_client.force_login(self.user)

    def test_create_post_form(self):
        """При отправке формы поста создается запись в БД"""
        posts_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'Тестовый текст',
        }
        response = self.authorized_client.post(reverse(
            'posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'Name'}))
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post_form(self):
        """При редактировании формы поста создается запись в БД"""
        form_data = {
            'group': self.group.id,
            'text': 'Редактированный текст',
        }
        response = self.authorized_client.post(reverse(
            'posts:post_edit', kwargs={'post_id': 1}),
            data=form_data,
            follow=True,
        )
        post_edit = response.context['post']
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': 1}))
        self.assertEqual(post_edit.text, form_data['text'])
