import uuid
import mongoengine as me
from datetime import datetime


class User(me.Document):
    ROLE_CHOICES = ('admin', 'host', 'player')

    id = me.UUIDField(primary_key=True, default=uuid.uuid4)
    username = me.StringField(required=True, unique=True, max_length=30)
    email = me.EmailField(required=True, unique=True)
    password = me.StringField(required=True)
    age = me.IntField(required=True, min_value=0)
    phone = me.StringField(max_length=20)
    role = me.StringField(choices=ROLE_CHOICES, default='player')
    is_active = me.BooleanField(default=True)
    is_staff = me.BooleanField(default=False)
    is_superuser = me.BooleanField(default=False)
    last_login = me.DateTimeField(default=None, null=True)

    meta = {
        'collection': 'users'
    }

    def __str__(self):
        return self.username


class AuditLog(me.Document):
    id = me.UUIDField(primary_key=True, default=uuid.uuid4)
    actor = me.ReferenceField(User, reverse_delete_rule=me.CASCADE)
    target = me.ReferenceField(User, null=True, reverse_delete_rule=me.NULLIFY)
    action = me.StringField(required=True)
    timestamp = me.DateTimeField(default=datetime.utcnow)

    meta = {
        'ordering': ['-timestamp'],
        'collection': 'audit_logs'
    }

    def __str__(self):
        return f'{self.timestamp} - {self.actor.username} - {self.action}'
