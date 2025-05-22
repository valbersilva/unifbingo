from rest_framework import serializers
from .models import User, AuditLog
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    age = serializers.IntegerField()
    phone = serializers.CharField()
    role = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True, allow_null=True)

    def create(self, validated_data):
        request = self.context.get('request')
        password = validated_data.pop('password', None)

        # Valores padrão
        role = 'player'
        is_staff = False
        is_superuser = False

        if request and request.user and request.user.is_authenticated:
            data = request.data
            role = data.get('role', 'player')
            is_staff = data.get('is_staff', False)
            is_superuser = data.get('is_superuser', False)

            if not request.user.is_superuser:
                is_superuser = False
            if not request.user.is_staff:
                is_staff = False
                role = 'player'

        hashed_password = make_password(password) if password else None

        user = User(
            password=hashed_password,
            role=role,
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_active=True,
            **validated_data
        )
        user.save()

        if request and request.user and request.user.is_authenticated:
            AuditLog(
                actor=request.user,
                target=user,
                action=f"Created user '{user.username}' with role '{user.role}'"
            ).save()

        return user

    def update(self, instance, validated_data):
        validated_data.pop('role', None)
        validated_data.pop('is_staff', None)
        validated_data.pop('is_superuser', None)

        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.password = make_password(password)

        instance.save()
        return instance


class AuditLogSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    actor_username = serializers.CharField(source='actor.username', read_only=True)
    target_username = serializers.CharField(source='target.username', read_only=True)
    action = serializers.CharField()
    timestamp = serializers.DateTimeField()
