import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

# Importar modelos e serializers se precisar interagir com o banco de dados
from .models import BingoRoom, RoomParticipant
from .serializers import BingoRoomSerializer, RoomParticipantSerializer

User = get_user_model()

class BingoRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # A sala de bingo será o 'group_name'
        self.room_name = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'bingo_room_{self.room_name}'

        # Verificação de autenticação (opcional, mas recomendado para jogos)
        # Você pode adaptar para JWT, se estiver usando no DRF
        if self.scope["user"].is_anonymous:
            await self.close()
            return

        # Adicionar o usuário ao grupo da sala
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Enviar informações iniciais da sala para o novo participante
        # (Ex: quando a sala inicia, estado atual, lista de jogadores)
        room_info = await self.get_room_details(self.room_name)
        if room_info:
            await self.send(text_data=json.dumps({
                'type': 'room_init',
                'room_details': room_info,
                'message': 'Bem-vindo à sala de bingo!'
            }))
            # Notificar outros participantes sobre o novo jogador
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'participant_joined',
                    'user_id': self.scope["user"].id,
                    'username': self.scope["user"].username,
                    'message': f'{self.scope["user"].username} entrou na sala.'
                }
            )

    async def disconnect(self, close_code):
        # Remover o usuário do grupo da sala
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        # Notificar outros participantes sobre a saída do jogador
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'participant_left',
                'user_id': self.scope["user"].id,
                'username': self.scope["user"].username,
                'message': f'{self.scope["user"].username} saiu da sala.'
            }
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'host_draw_number':
            # Apenas o host pode sortear números
            # Você precisará de lógica para verificar se o usuário é o host da sala
            is_host = await self.is_user_room_host(self.room_name, self.scope["user"])
            if is_host:
                drawn_number = await self.draw_new_number(self.room_name)
                if drawn_number is not None:
                    # Enviar o número sorteado para todos na sala
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'number_drawn',
                            'number': drawn_number,
                            'message': f'Número sorteado: {drawn_number}'
                        }
                    )
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Apenas o host pode sortear números.'
                }))
        elif message_type == 'start_game':
            is_host = await self.is_user_room_host(self.room_name, self.scope["user"])
            if is_host:
                await self.start_game_session(self.room_name)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_started',
                        'message': 'O jogo começou! Boa sorte!'
                    }
                )
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Apenas o host pode iniciar o jogo.'
                }))
        # Outras ações como 'bingo_declared', 'chat_message', etc.

    # --- Funções para enviar mensagens para o grupo ---
    async def number_drawn(self, event):
        # Recebe o evento do channel layer e envia para o WebSocket
        number = event['number']
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'number_drawn',
            'number': number,
            'message': message
        }))

    async def game_started(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'game_started',
            'message': message
        }))

    async def participant_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'participant_joined',
            'user_id': event['user_id'],
            'username': event['username'],
            'message': event['message']
        }))

    async def participant_left(self, event):
        await self.send(text_data=json.dumps({
            'type': 'participant_left',
            'user_id': event['user_id'],
            'username': event['username'],
            'message': event['message']
        }))

    # --- Funções assíncronas para interação com o banco de dados ---
    @database_sync_to_async
    def get_room_details(self, room_id):
        try:
            room = BingoRoom.objects.get(id=room_id)
            # Você pode usar um serializer do DRF aqui para formatar os dados
            serializer = BingoRoomSerializer(room)
            return serializer.data
        except BingoRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def is_user_room_host(self, room_id, user):
        try:
            room = BingoRoom.objects.get(id=room_id)
            return room.host == user
        except BingoRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def draw_new_number(self, room_id):
        # Implemente a lógica para sortear um número,
        # atualizando o GameSession associado à sala.
        # Exemplo simplificado:
        try:
            room = BingoRoom.objects.get(id=room_id)
            # Supondo que você tenha um modelo GameSession para gerenciar o jogo em andamento
            game_session = room.active_game_session # Você precisaria adicionar isso ao modelo BingoRoom ou buscar de outra forma
            if not game_session:
                return None # Ou levantar um erro

            # Lógica para sortear um número único não sorteado
            # (Isso deve ser mais robusto, com controle de números já sorteados)
            import random
            drawn_number = random.randint(1, 75) # Exemplo

            # Salvar o número sorteado no game_session (ex: lista de números sorteados)
            # game_session.drawn_numbers.append(drawn_number) # Atualizar campo JSONField ou similar
            # game_session.save()

            return drawn_number
        except BingoRoom.DoesNotExist:
            return None
        except Exception as e:
            print(f"Erro ao sortear número: {e}")
            return None

    @database_sync_to_async
    def start_game_session(self, room_id):
        # Lógica para iniciar uma nova sessão de jogo para a sala
        # e associá-la à BingoRoom
        try:
            room = BingoRoom.objects.get(id=room_id)
            if not room.is_closed: # A sala deve estar aberta para iniciar
                # Criar uma nova GameSession e associá-la à sala
                # Exemplo: game_session = GameSession.objects.create(room=room, status='started')
                # room.active_game_session = game_session # Ou atualize o campo
                # room.save()
                return True
            return False
        except BingoRoom.DoesNotExist:
            return False