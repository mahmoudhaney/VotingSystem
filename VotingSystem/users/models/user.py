from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from django.db import models

class User(AbstractUser):
    address = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=11, null=True, blank=True)
    id_proof_number = models.CharField(max_length=14, null=False, blank=False, unique=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['phone_number'], condition=Q(phone_number__isnull=False), name='unique_phone_number'),
        ]

    def __str__(self) -> str:
        return str(self.username)
