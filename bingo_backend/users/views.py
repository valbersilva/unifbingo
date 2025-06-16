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
        # Allow creation without authentication, but protect all other actions
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdmin()]

    def perform_create(self, serializer):
        request_user = self.request.user

        if not request_user.is_authenticated:
            # If not authenticated: force new user as player
            serializer.save(
                role='player',
                is_staff=False,
                is_superuser=False
            )
        else:
            # Authenticated user creating
            data = self.request.data

            # By default, any user creates only players
            role = data.get('role', 'player')
            is_staff = data.get('is_staff', False)
            is_superuser = data.get('is_superuser', False)

            # Non-admin users cannot create staff or superusers
            if not request_user.is_superuser:
                is_superuser = False
            if not request_user.is_staff:
                is_staff = False
                role = 'player'

            serializer.save(
                role=role,
                is_staff=is_staff,
                is_superuser=is_superuser
            )

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsAdmin])
    def set_role(self, request, pk=None):
        """
        Custom action to change user role.
        """
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

    def retrieve(self, request, *args, **kwargs):
        """
        Fix for GET /api/users/{user_id}/ to avoid listing all users on detail view.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


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
