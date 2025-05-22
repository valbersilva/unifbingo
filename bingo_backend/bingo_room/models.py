from mongoengine import (
    Document, EmbeddedDocument, StringField, ListField, 
    ReferenceField, DateTimeField, BooleanField, EmbeddedDocumentField, UUIDField, IntField
)
import uuid
from datetime import datetime

class RoomParticipant(EmbeddedDocument):
    user_id = StringField(required=True)  # armazene o id do usuário (string)
    username = StringField(required=True)
    joined_at = DateTimeField(default=datetime.utcnow)

class BingoCard(Document):
    meta = {'collection': 'bingocards'}
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    room = StringField(required=True)  # ID da sala (string)
    owner_id = StringField(required=True)  # ID do dono da cartela
    numbers = ListField(ListField(IntField()), required=True)  # matriz 5x5 de números
    card_hash = StringField(required=True)

class BingoRoom(Document):
    meta = {'collection': 'bingorooms'}
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    room_code = StringField(max_length=10, unique=True)
    created_by_id = StringField(required=True)  # ID do usuário criador
    participants = ListField(EmbeddedDocumentField(RoomParticipant))
    is_closed = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
