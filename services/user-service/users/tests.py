from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.cache import cache

from .models import CustomPermission

User = get_user_model()


class UserApiTests(APITestCase):
    def setUp(self) -> None:
        self.superuser = User.objects.create_superuser(first_name='ok', last_name='ok', email='ok@ok.com', password='ok')
        self.user = User.objects.create_user(first_name='test', last_name='test', email='test@test.com', password='test')

        self.client.force_authenticate(user=self.superuser)

    def test_me(self):
        response = self.client.get(reverse('users:me'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('first_name'), 'ok')
        self.assertEqual(response.data.get('last_name'), 'ok')
        self.assertEqual(response.data.get('email'), 'ok@ok.com')

    def test_user_detail(self):
        url = reverse('users:read_users-detail', kwargs={'pk': self.user.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('first_name'), 'test')
        self.assertEqual(response.data.get('last_name'), 'test')
        self.assertEqual(response.data.get('email'), 'test@test.com')

    def test_user_list(self):
        url = reverse('users:read_users-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_update_user(self):
        url = reverse('users:update', kwargs={'pk': self.user.pk})
        response = self.client.patch(url, data={'first_name': 'clown'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('first_name'), 'clown')

    def test_create_user(self):
        url = reverse('users:create')
        data = {
            'first_name': 'test2', 'last_name': 'test2',
            'email': 'test2@test2.com',
            'password': 'test2', 'confirm_password': 'test2'
        }
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data.get('first_name'), 'test2')
        self.assertEqual(response.data.get('last_name'), 'test2')
        self.assertEqual(response.data.get('email'), 'test2@test2.com')

    def test_fail_create_user(self):
        url = reverse('users:create')
        data = {
            'first_name': 'jon', 'last_name': 'duo',
            'email': 'ok@ok.com',
            'password': 'test2', 'confirm_password': 'test2'
        }
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_user(self):
        url = reverse('users:delete', kwargs={'pk': self.user.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        qs = User.objects.filter(pk=self.user.pk)
        self.assertTrue(qs.exists())
        self.assertEqual(qs.first().is_deleted, True)


# ========================================================
# Role and Permissions Tests
# ========================================================
class PermissionApiTest(APITestCase):
    def setUp(self) -> None:
        self.superuser = User.objects.create_superuser(first_name='ok', last_name='ok', email='ok@ok.com', password='ok')
        self.client.force_authenticate(user=self.superuser)

        self.permission = CustomPermission.objects.create(
            name='test:test',
            description='for test purposes'
        )

    def test_permission_detail(self):
        url = reverse('users:permissions-detail', kwargs={'pk': self.permission.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('name'), 'test:test')

    def test_permission_list(self):
        url = reverse('users:permissions-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_cache(self):
        url = reverse('users:permissions-list')

        with self.assertNumQueries(1):
            self.client.get(url)

        with self.assertNumQueries(0):
            self.client.get(url)

    def test_cache_directly(self):
        cache.clear()
        url = reverse('users:permissions-list')
        cache_key = 'users:permissions:all'

        self.client.get(url)

        self.assertNotEqual(cache.get(cache_key, default=None), None)
