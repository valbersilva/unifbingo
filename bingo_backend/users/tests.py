from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User
from django.contrib.auth.hashers import make_password


class UserAPITestCase(APITestCase):
    def setUp(self):
        # Cria usuários manualmente
        self.admin = User(
            username='admin1',
            email='admin@example.com',
            password=make_password('admin123'),
            role='admin',
            is_superuser=True,
            is_staff=True,
            age=30,
            phone='123456789'
        )
        self.admin.save()

        self.player = User(
            username='player1',
            email='player@example.com',
            password=make_password('player123'),
            role='player',
            is_superuser=False,
            is_staff=False,
            age=25,
            phone='987654321'
        )
        self.player.save()

        # Login do admin
        response = self.client.post(reverse('custom-login'), {
            'username': 'admin1',
            'password': 'admin123'
        })
        self.admin_token = response.data['token']

        # Login do player
        response = self.client.post(reverse('custom-login'), {
            'username': 'player1',
            'password': 'player123'
        })
        self.player_token = response.data['token']

    def test_user_creation(self):
        response = self.client.post(reverse('user-list'), {
            "username": "newuser",
            "password": "test123",
            "email": "new@example.com",
            "age": 30,
            "phone": "+559999999999"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects(username='newuser').first() is not None)

    def test_admin_can_list_users(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_player_cannot_list_users(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.player_token)
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_change_role(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)
        url = reverse('user-set-role', kwargs={'pk': str(self.player.id)})
        response = self.client.patch(url, {"role": "host"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        player = User.objects.get(id=self.player.id)
        self.assertEqual(player.role, "host")

    def test_player_cannot_change_role(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.player_token)
        url = reverse('user-set-role', kwargs={'pk': str(self.admin.id)})
        response = self.client.patch(url, {"role": "player"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_returns_token(self):
        response = self.client.post(reverse('custom-login'), {
            'username': 'player1',
            'password': 'player123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
