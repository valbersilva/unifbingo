from rest_framework import serializers
from .models import User, AuditLog


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'read_only': True},
            'is_staff': {'read_only': True},
            'is_superuser': {'read_only': True},
        }

    def create(self, validated_data):
        request = self.context.get('request')
        password = validated_data.pop('password', None)

        # Inicializa com valores padrão
        role = 'player'
        is_staff = False
        is_superuser = False

        # Se for um request autenticado:
        if request and request.user.is_authenticated:
            data = request.data
            role = data.get('role', 'player')
            is_staff = data.get('is_staff', False)
            is_superuser = data.get('is_superuser', False)

            # Superuser pode tudo
            if not request.user.is_superuser:
                is_superuser = False

            # Staff pode criar outros staff, mas não admin
            if not request.user.is_staff:
                is_staff = False
                role = 'player'

        user = User(**validated_data)
        user.role = role
        user.is_staff = is_staff
        user.is_superuser = is_superuser

        if password:
            user.set_password(password)
        user.save()

        # Registra no audit log se o criador for autenticado
        if request and request.user.is_authenticated:
            AuditLog.objects.create(
                actor=request.user,
                target=user,
                action=f"Created user '{user.username}' with role '{user.role}'"
            )

        return user

    def update(self, instance, validated_data):
        validated_data.pop('role', None)
        validated_data.pop('is_staff', None)
        validated_data.pop('is_superuser', None)

        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class AuditLogSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source='actor.username', read_only=True)
    target_username = serializers.CharField(source='target.username', read_only=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'actor_username', 'target_username', 'action', 'timestamp']
