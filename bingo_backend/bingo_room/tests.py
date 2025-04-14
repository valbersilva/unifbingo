from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from .models import BingoRoom, RoomParticipant, BingoCard


class BingoRoomAPITestCase(APITestCase):

    def setUp(self):
        # Cria usuários
        self.host = User.objects.create_user(username='host1', password='host123', role='host', email='host@example.com')
        self.player = User.objects.create_user(username='player1', password='player123', role='player', email='player@example.com')

        # Login e tokens
        res = self.client.post(reverse('custom-login'), {'username': 'host1', 'password': 'host123'})
        self.host_token = res.data['token']

        res = self.client.post(reverse('custom-login'), {'username': 'player1', 'password': 'player123'})
        self.player_token = res.data['token']

    def test_host_can_create_room(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.host_token)
        response = self.client.post(reverse('bingoroom-list'))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('room_code' in response.data)

    def test_player_cannot_create_room(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.player_token)
        response = self.client.post(reverse('bingoroom-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_player_can_join_room(self):
        # Host cria sala
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.host_token)
        room_response = self.client.post(reverse('bingoroom-list'))
        room_id = room_response.data['id']

        # Player entra na sala
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.player_token)
        response = self.client.post(reverse('join-room'), {"room": room_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(RoomParticipant.objects.filter(user=self.player, room__id=room_id).exists(), True)

    def test_player_can_leave_room(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.host_token)
        room = self.client.post(reverse('bingoroom-list')).data

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.player_token)
        self.client.post(reverse('join-room'), {"room": room["id"]})

        response = self.client.delete(reverse('leave-room'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(RoomParticipant.objects.filter(user=self.player).exists())

    def test_player_can_create_card(self):
        # Host cria sala
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.host_token)
        room = self.client.post(reverse('bingoroom-list')).data

        # Player entra na sala
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.player_token)
        self.client.post(reverse('join-room'), {"room": room["id"]})

        # Cria cartela
        response = self.client.post(reverse('bingocard-list'), {"room": room["id"]})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue("card_hash" in response.data)
        self.assertEqual(BingoCard.objects.filter(owner=self.player).count(), 1)

    def test_player_cannot_create_card_without_joining(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.host_token)
        room = self.client.post(reverse('bingoroom-list')).data

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.player_token)
        response = self.client.post(reverse('bingocard-list'), {"room": room["id"]})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
