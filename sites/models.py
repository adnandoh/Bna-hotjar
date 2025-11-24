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
    
    # Connection status tracking
    is_connected = models.BooleanField(default=False)
    last_activity_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name
    
    @property
    def connection_status(self):
        """
        Returns the connection status based on last activity
        - 'connected': Activity within last 5 minutes
        - 'inactive': Activity older than 5 minutes
        - 'never_connected': No activity recorded
        """
        if not self.last_activity_at:
            return 'never_connected'
        
        from django.utils import timezone
        from datetime import timedelta
        
        time_since_activity = timezone.now() - self.last_activity_at
        if time_since_activity < timedelta(minutes=5):
            return 'connected'
        else:
            return 'inactive'
