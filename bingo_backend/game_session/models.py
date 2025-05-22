from mongoengine import (
    Document,
    StringField,
    ReferenceField,
    ListField,
    IntField,
    BooleanField,
    DateTimeField,
    CASCADE,
    DictField,
)
from datetime import datetime
from bingo_room.models import BingoRoom
from users.models import User
from bingo_room.models import BingoCard


class GameSession(Document):
    room = ReferenceField(BingoRoom, reverse_delete_rule=CASCADE, required=True)
    winner = ReferenceField(User, null=True)
    winning_card = ReferenceField(BingoCard, null=True)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'game_sessions',
        'ordering': ['-created_at'],
    }

    @property
    def draws(self):
        return DrawnNumber.objects(session=self)


class DrawnNumber(Document):
    session = ReferenceField(GameSession, reverse_delete_rule=CASCADE, required=True)
    number = IntField(min_value=1, max_value=75, required=True)

    meta = {
        'collection': 'drawn_numbers',
        'indexes': [
            {'fields': ['session', 'number'], 'unique': True},
        ]
    }


class GameAuditLog(Document):
    session = ReferenceField(GameSession, reverse_delete_rule=CASCADE)
    actor = ReferenceField(User)
    action = StringField(required=True)
    timestamp = DateTimeField(default=datetime.utcnow)
    target = ReferenceField(User, null=True)

    meta = {
        'collection': 'game_audit_logs',
        'ordering': ['-timestamp'],
    }


class GameHistory(Document):
    session = ReferenceField(GameSession, reverse_delete_rule=CASCADE)
    room_code = StringField(required=True)
    winner = ReferenceField(User)
    winning_card_hash = StringField(null=True)
    drawn_numbers = ListField(IntField())
    started_at = DateTimeField()
    is_completed = BooleanField(default=False)

    meta = {
        'collection': 'game_history',
        'ordering': ['-started_at'],
    }
