import uuid
from django.db import models
from events.models import Session

class Recording(models.Model):
    recording_id = models.CharField(max_length=255, unique=True)
    session = models.ForeignKey('events.Session', on_delete=models.CASCADE)
    duration = models.IntegerField(default=0)  # in seconds
    event_count = models.IntegerField(default=0)
    recording_data = models.JSONField(default=list, blank=True)  # rrweb events
    has_errors = models.BooleanField(default=False)
    has_rage_clicks = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Recording {self.recording_id}"
