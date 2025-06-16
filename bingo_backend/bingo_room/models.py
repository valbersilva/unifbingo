from django.db import models
from users.models import User, AuditLog
import uuid
import random
import string
import hashlib


def generate_room_code():
    """
    Generates a unique room code in the format 'ABC-123'.
    """
    left = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    right = ''.join(random.choices(string.digits, k=3))
    return f"{left}-{right}"


class BingoRoom(models.Model):
    """
    Represents a bingo game room created by a host or admin.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room_code = models.CharField(max_length=7, unique=True, default=generate_room_code)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    is_closed = models.BooleanField(default=False)  # NOVO CAMPO: indica se a sala está fechada

    def __str__(self):
        return self.room_code


class RoomParticipant(models.Model):
    """
    Represents the current room a player has joined.
    Only one room per user at a time (OneToOneField).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='current_room')
    room = models.ForeignKey(BingoRoom, on_delete=models.CASCADE, related_name='participants')
    joined_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """
        Save and create audit log for room join.
        """
        super().save(*args, **kwargs)
        AuditLog.objects.create(
            actor=self.user,
            action=f"Joined room {self.room.room_code}",
            target=None
        )

    def delete(self, *args, **kwargs):
        """
        Delete and create audit log for room leave.
        """
        AuditLog.objects.create(
            actor=self.user,
            action=f"Left room {self.room.room_code}",
            target=None
        )
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} in room {self.room.room_code}"


class BingoCard(models.Model):
    """
    Represents a player's bingo card in a room.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    card_hash = models.CharField(max_length=64, unique=True, editable=False)
    room = models.ForeignKey(BingoRoom, on_delete=models.CASCADE, related_name='cards')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cards')
    numbers = models.JSONField()  # Store 5x5 bingo matrix
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_numbers(self):
        """
        Generates a random bingo card with the standard 5x5 format.
        Each column corresponds to a specific range of numbers:
        - B: 1-15
        - I: 16-30
        - N: 31-45 (with a free space in the middle)
        - G: 46-60
        - O: 61-75
        """
        card_columns = []
        # Define os intervalos de números para cada coluna
        ranges = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]

        for i, col_range in enumerate(ranges):
            # A coluna do meio (índice 2) é a coluna "N"
            if i == 2:
                # Gera 4 números para a coluna "N"
                numbers = random.sample(range(col_range[0], col_range[1] + 1), 4)
                # Adiciona o espaço livre 'X' na posição do meio
                column = numbers[:2] + ['X'] + numbers[2:]
            else:
                # Gera 5 números para as outras colunas
                column = random.sample(range(col_range[0], col_range[1] + 1), 5)
            
            card_columns.append(column)
        
        # Transpõe as colunas em linhas para formar a cartela final
        # A função zip(*list_of_lists) é uma forma eficiente de fazer essa transposição
        return [list(row) for row in zip(*card_columns)]

    def save(self, *args, **kwargs):
        if not self.numbers:
            self.numbers = self.generate_numbers()
        if not self.card_hash:
            raw_data = str(self.numbers) + str(self.owner_id) + str(self.room_id)
            self.card_hash = hashlib.sha256(raw_data.encode()).hexdigest()
        super().save(*args, **kwargs)

        if not AuditLog.objects.filter(action__icontains=self.card_hash).exists():
            AuditLog.objects.create(
                actor=self.owner,
                action=f"Generated BingoCard for room {self.room.room_code} with hash {self.card_hash}",
                target=None
            )

    def __str__(self):
        return f"Card {self.card_hash[:8]}... for {self.owner.username}"
