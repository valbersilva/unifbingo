from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from .models import User, AuditLog
from .serializers import UserSerializer, AuditLogSerializer
from .permissions import IsAdmin


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        # Permite criação sem autenticação, mas protege o resto
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdmin()]

    def perform_create(self, serializer):
        request_user = self.request.user

        if not request_user.is_authenticated:
            # Caso não esteja autenticado: forçar usuário comum
            serializer.save(
                role='player',
                is_staff=False,
                is_superuser=False
            )
        else:
            # Está autenticado
            data = self.request.data

            # Por padrão, qualquer usuário cria apenas player
            role = data.get('role', 'player')
            is_staff = data.get('is_staff', False)
            is_superuser = data.get('is_superuser', False)

            # Se não for admin, força limites:
            if not request_user.is_superuser:
                is_superuser = False  # só superuser pode criar outro superuser
            if not request_user.is_staff:
                is_staff = False  # só staff pode criar outro staff
                role = 'player'  # forçar papel básico

            serializer.save(
                role=role,
                is_staff=is_staff,
                is_superuser=is_superuser
            )

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsAdmin])
    def set_role(self, request, pk=None):
        user = self.get_object()
        new_role = request.data.get('role')

        valid_roles = ['admin', 'host', 'player']
        if new_role not in valid_roles:
            return Response({'detail': 'Invalid role.'}, status=status.HTTP_400_BAD_REQUEST)

        old_role = user.role
        user.role = new_role
        user.save()

        AuditLog.objects.create(
            actor=request.user,
            target=user,
            action=f"Changed role from {old_role} to {new_role}"
        )

        return Response({'detail': f'Role updated to {new_role} successfully.'})


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
        })
