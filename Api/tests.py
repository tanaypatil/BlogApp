import io

from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from Api.models import Blog, Tag, Comment

User = get_user_model()


def get_temporary_image():
    image = Image.new('RGB', (100, 100))
    tmp_file = io.BytesIO()
    image.save(tmp_file, 'png')
    tmp_file.seek(0)
    return SimpleUploadedFile('test.png', tmp_file.read(), content_type='image/png')


class BlogUserApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            bio='Test bio',
            profile_picture=get_temporary_image()
        )
        self.client = APIClient()

    def test_create_user(self):
        url = reverse('users')
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'bio': 'New bio',
            'profile_picture': get_temporary_image()
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_retrieve_user_authenticated(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('users')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)

    def test_update_user(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('users')
        data = {'bio': 'Updated bio'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.bio, 'Updated bio')

    def test_delete_user(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('users')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_create_user_unauthenticated_only(self):
        # Authenticated user should not be able to create another user
        self.client.force_authenticate(user=self.user)
        url = reverse('users')
        data = {
            'username': 'failuser',
            'email': 'fail@example.com',
            'password': 'failpass',
            'bio': 'fail',
            'profile_picture': get_temporary_image()
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_user_unauthenticated(self):
        url = reverse('users')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_unauthenticated(self):
        url = reverse('users')
        data = {'bio': 'Should not update'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_user_unauthenticated(self):
        url = reverse('users')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BlogApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='blogger',
            email='blogger@example.com',
            password='blogpass',
            bio='Blogger bio',
            profile_picture=get_temporary_image()
        )
        self.tag = Tag.objects.create(name='django')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_blog(self):
        url = '/blogs/'
        data = {
            'title': 'Test Blog',
            'body': 'Blog content',
            'category': 'TECHNOLOGY',
            'tags': [{'name': 'django'}]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Blog.objects.count(), 1)
        self.assertEqual(Blog.objects.first().author, self.user)

    def test_list_blogs(self):
        Blog.objects.create(title='Blog1', body='Body1', author=self.user, category='TECHNOLOGY')
        url = '/blogs/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_update_blog(self):
        blog = Blog.objects.create(title='Blog2', body='Body2', author=self.user, category='TECHNOLOGY')
        url = f'/blogs/{blog.slug}/'
        data = {'title': 'Updated Blog2'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        blog.refresh_from_db()
        self.assertEqual(blog.title, 'Updated Blog2')

    def test_delete_blog(self):
        blog = Blog.objects.create(title='Blog3', body='Body3', author=self.user, category='TECHNOLOGY')
        url = f'/blogs/{blog.slug}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Blog.objects.filter(id=blog.id).exists())

    def test_blog_permissions(self):
        other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='otherpass',
            bio='Other bio',
            profile_picture=get_temporary_image()
        )
        blog = Blog.objects.create(title='Blog4', body='Body4', author=other_user, category='TECHNOLOGY')
        blog.refresh_from_db()  # Ensure slug is generated
        self.client.force_authenticate(user=self.user)
        url = f'/blogs/{blog.slug}/'
        response = self.client.patch(url, {'title': 'Hacked'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_blog_unauthenticated(self):
        self.client.force_authenticate(user=None)
        url = '/blogs/'
        data = {
            'title': 'NoAuth',
            'body': 'NoAuth',
            'category': 'TECHNOLOGY',
            'tags': [{'name': 'django'}]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_blog_unauthorized(self):
        other_user = User.objects.create_user(
            username='otheruser',
            email='otheruser@example.com',
            password='otherpass',
            bio='Other bio',
            profile_picture=get_temporary_image()
        )
        blog = Blog.objects.create(title='OtherBlog', body='Body', author=other_user, category='TECHNOLOGY')
        url = f'/blogs/{blog.id}/'
        response = self.client.patch(url, {'title': 'Should not update'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_blog_unauthorized(self):
        other_user = User.objects.create_user(
            username='otheruser2',
            email='otheruser2@example.com',
            password='otherpass2',
            bio='Other bio2',
            profile_picture=get_temporary_image()
        )
        blog = Blog.objects.create(title='OtherBlog2', body='Body', author=other_user, category='TECHNOLOGY')
        url = f'/blogs/{blog.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_blogs_unauthenticated(self):
        self.client.force_authenticate(user=None)
        url = '/blogs/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CommentApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='commenter',
            email='commenter@example.com',
            password='commentpass',
            bio='Commenter bio',
            profile_picture=get_temporary_image()
        )
        self.blog = Blog.objects.create(title='Blog', body='Body', author=self.user, category='TECHNOLOGY')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_comment(self):
        url = '/comments/'
        data = {'blog': self.blog.id, 'text': 'Nice post!'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.first().user, self.user)

    def test_list_comments(self):
        Comment.objects.create(user=self.user, blog=self.blog, text='First!')
        url = '/comments/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_update_comment(self):
        comment = Comment.objects.create(user=self.user, blog=self.blog, text='Edit me')
        url = f'/comments/{comment.id}/'
        data = {'text': 'Edited'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()
        self.assertEqual(comment.text, 'Edited')

    def test_delete_comment(self):
        comment = Comment.objects.create(user=self.user, blog=self.blog, text='Delete me')
        url = f'/comments/{comment.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=comment.id).exists())

    def test_comment_permissions(self):
        other_user = User.objects.create_user(
            username='other2',
            email='other2@example.com',
            password='other2pass',
            bio='Other2 bio',
            profile_picture=get_temporary_image()
        )
        comment = Comment.objects.create(user=other_user, blog=self.blog, text='Not yours')
        url = f'/comments/{comment.id}/'
        response = self.client.patch(url, {'text': 'Hacked'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_comment_unauthenticated(self):
        self.client.force_authenticate(user=None)
        url = '/comments/'
        data = {'blog': self.blog.id, 'text': 'NoAuth'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_comment_unauthorized(self):
        other_user = User.objects.create_user(
            username='othercomment',
            email='othercomment@example.com',
            password='othercommentpass',
            bio='Other comment bio',
            profile_picture=get_temporary_image()
        )
        comment = Comment.objects.create(user=other_user, blog=self.blog, text='Not yours')
        url = f'/comments/{comment.id}/'
        response = self.client.patch(url, {'text': 'Should not update'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_comment_unauthorized(self):
        other_user = User.objects.create_user(
            username='othercomment2',
            email='othercomment2@example.com',
            password='othercommentpass2',
            bio='Other comment bio2',
            profile_picture=get_temporary_image()
        )
        comment = Comment.objects.create(user=other_user, blog=self.blog, text='Not yours 2')
        url = f'/comments/{comment.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_comments_unauthenticated(self):
        self.client.force_authenticate(user=None)
        url = '/comments/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
