import uuid
from django.db import models
from sites.models import Site

class Session(models.Model):
    session_id = models.UUIDField(default=uuid.uuid4, unique=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    user_identifier = models.CharField(max_length=255, null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    device_type = models.CharField(max_length=50)
    browser = models.CharField(max_length=100)
    os = models.CharField(max_length=100)
    location = models.JSONField(null=True) # Country, city from IP
    viewport = models.JSONField() # Width, height
    tags = models.JSONField(default=list)

    def __str__(self):
        return f"Session {self.session_id} - {self.site.name}"

class Event(models.Model):
    EVENT_TYPES = [
        ('click', 'Click'),
        ('scroll', 'Scroll'),
        ('mouse_move', 'Mouse Move'),
        ('form_interaction', 'Form Interaction'),
        ('page_view', 'Page View'),
        ('custom', 'Custom Event'),
        ('rage_click', 'Rage Click'),
        ('error', 'Error'),
    ]
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    timestamp = models.DateTimeField()
    page_url = models.TextField()
    data = models.JSONField()  # Event-specific data

    class Meta:
        indexes = [
            models.Index(fields=['session', 'timestamp']),
            models.Index(fields=['page_url', 'event_type']),
        ]

    def __str__(self):
        return f"{self.event_type} at {self.timestamp}"
