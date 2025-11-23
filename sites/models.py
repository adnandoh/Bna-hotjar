import uuid
from django.db import models
from django.contrib.auth.models import User

class Site(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, unique=True)
    tracking_id = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    settings = models.JSONField(default=dict) # Privacy, sampling rate, etc.

    def __str__(self):
        return self.name
