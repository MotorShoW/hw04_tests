from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostsUrlTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Name')
        Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        Post.objects.create(
            author=cls.user,
            text='Тест текст'
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = PostsUrlTest.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_exists_at_desired_location(self):
        """Проверка работоспособности URL"""
        url_names = [
            '/',
            '/group/test-slug/',
            '/profile/Name/',
            '/posts/1/',
        ]
        for url in url_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_post_id_authorized_author_url(self):
        """Проверка доступа автора на редактирование поста"""
        response = self.authorized_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, 200)

    def test_create_url_authorized(self):
        """Проверка доступа авторизованного пользователя к созданию поста"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_unexisting_url(self):
        """Проверка несуществующей страницы на 404"""
        response = self.guest_client.get('/unexisting/')
        self.assertEqual(response.status_code, 404)

    def test_urls_uses_correct_templates(self):
        """Проверка использования правильных шаблонов"""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/Name/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
