from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User


class UserAPITestCase(APITestCase):

    def setUp(self):
        # Create an admin and a player
        self.admin = User.objects.create_user(username='admin1', password='admin123', role='admin', email='admin@example.com')
        self.player = User.objects.create_user(username='player1', password='player123', role='player', email='player@example.com')

        # Get admin token
        response = self.client.post(reverse('custom-login'), {
            'username': 'admin1',
            'password': 'admin123'
        })
        self.admin_token = response.data['token']

        # Get player token
        response = self.client.post(reverse('custom-login'), {
            'username': 'player1',
            'password': 'player123'
        })
        self.player_token = response.data['token']

    def test_user_creation(self):
        # Anyone can create user
        response = self.client.post(reverse('user-list'), {
            "username": "newuser",
            "password": "test123",
            "email": "new@example.com",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(username='newuser').exists(), True)

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
        url = reverse('user-set-role', kwargs={'pk': self.player.id})
        response = self.client.patch(url, {"role": "host"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.player.refresh_from_db()
        self.assertEqual(self.player.role, "host")

    def test_player_cannot_change_role(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.player_token)
        url = reverse('user-set-role', kwargs={'pk': self.admin.id})
        response = self.client.patch(url, {"role": "player"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_returns_token(self):
        response = self.client.post(reverse('custom-login'), {
            'username': 'player1',
            'password': 'player123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
