from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from bingo_room.models import BingoRoom, RoomParticipant, BingoCard
from game_session.models import GameSession, DrawnNumber, GameHistory


class GameSessionAPITestCase(APITestCase):

    def setUp(self):
        # Criação de usuários
        self.host = User.objects.create_user(username='host1', password='host123', role='host', email='host@example.com')
        self.player = User.objects.create_user(username='player1', password='player123', role='player', email='player@example.com')

        # Login e tokens
        res = self.client.post(reverse('custom-login'), {'username': 'host1', 'password': 'host123'})
        self.host_token = res.data['token']

        res = self.client.post(reverse('custom-login'), {'username': 'player1', 'password': 'player123'})
        self.player_token = res.data['token']

        # Host cria sala
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.host_token)
        self.room = self.client.post(reverse('bingoroom-list')).data

        # Player entra na sala
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.player_token)
        self.client.post(reverse('join-room'), {"room": self.room["id"]})

        # Player cria cartela
        self.card = self.client.post(reverse('bingocard-list'), {"room": self.room["id"]}).data

        # Host cria sessão
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.host_token)
        self.session = self.client.post(reverse('game-session-list'), {"room": self.room["id"]}).data

    def test_draw_next_number(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.host_token)
        response = self.client.post(reverse('game-session-draw-next', args=[self.session["id"]]))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(DrawnNumber.objects.filter(session_id=self.session["id"]).exists())

    def test_validate_bingo_invalid(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.player_token)
        response = self.client.post(reverse('game-session-validate-bingo', args=[self.session["id"]]))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validate_bingo_valid_by_row(self):
        from game_session.models import DrawnNumber
        # Força os números da primeira linha da cartela como sorteados
        card_obj = BingoCard.objects.get(id=self.card["id"])
        numbers = card_obj.numbers[0]  # primeira linha
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.host_token)
        for number in numbers:
            if number != 0:
                DrawnNumber.objects.create(session_id=self.session["id"], number=number)

        # Player valida BINGO
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.player_token)
        response = self.client.post(reverse('game-session-validate-bingo', args=[self.session["id"]]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("BINGO", response.data["detail"])

    def test_end_game_session_manually(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.host_token)
        response = self.client.post(reverse('game-session-end', args=[self.session["id"]]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(GameSession.objects.get(id=self.session["id"]).is_active, False)

    def test_history_created_after_bingo(self):
        from game_session.models import DrawnNumber
        card_obj = BingoCard.objects.get(id=self.card["id"])
        numbers = card_obj.numbers[0]  # linha
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.host_token)
        for number in numbers:
            if number != 0:
                DrawnNumber.objects.create(session_id=self.session["id"], number=number)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.player_token)
        self.client.post(reverse('game-session-validate-bingo', args=[self.session["id"]]))

        self.assertTrue(GameHistory.objects.filter(session_id=self.session["id"]).exists())

    def test_block_second_winner(self):
        from game_session.models import DrawnNumber
        card_obj = BingoCard.objects.get(id=self.card["id"])
        numbers = card_obj.numbers[0]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.host_token)
        for number in numbers:
            if number != 0:
                DrawnNumber.objects.create(session_id=self.session["id"], number=number)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.player_token)
        self.client.post(reverse('game-session-validate-bingo', args=[self.session["id"]]))

        # Tenta validar de novo
        response = self.client.post(reverse('game-session-validate-bingo', args=[self.session["id"]]))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already been declared", response.data["detail"])
