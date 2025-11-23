from django.db import models
from sites.models import Site

class Funnel(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    steps = models.JSONField() # List of steps: [{name: 'Landing', url: '/'}, ...]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
