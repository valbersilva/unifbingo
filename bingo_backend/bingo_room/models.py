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
        Generate a 5x5 bingo card matrix with numbers in columns:
        B: 1-15, I: 16-30, N: 31-45, G: 46-60, O: 61-75
        The center (N[2]) is a free space (0).
        """
        card = []
        columns = [range(1, 16), range(16, 31), range(31, 46), range(46, 61), range(61, 76)]
        for col_range in columns:
            column_numbers = random.sample(col_range, 5)
            card.append(column_numbers)
        card[2][2] = 0  # free space in the center
        return [list(row) for row in zip(*card)]  # transpose to rows

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
