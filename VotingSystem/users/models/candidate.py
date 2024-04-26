from django.db import models
from .user import User
import uuid

def candidate_image_upload(instance, file_name):
    image_name, extension = file_name.split(".")
    return f"candidates_imgs/{str(uuid.uuid4())}.{extension}"

class Candidate(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    photo = models.ImageField(upload_to=candidate_image_upload)
    bio = models.TextField(max_length=500, null=True, blank=True)
    admin = models.ForeignKey(User, related_name='admin', on_delete=models.CASCADE)
    election = models.ForeignKey('elections.Election', related_name='candidates', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_votes = models.PositiveIntegerField(default=0)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self) -> str:
        return str(self.name)