from django.db import models
from sites.models import Site

class FormAnalytics(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    form_id = models.CharField(max_length=255)  # CSS selector or form identifier
    page_url = models.TextField()
    field_analytics = models.JSONField()  # Field-level metrics
    completion_rate = models.FloatField(default=0.0)
    abandonment_rate = models.FloatField(default=0.0)
    avg_time_to_complete = models.IntegerField(default=0)  # In seconds
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Form Analytics: {self.form_id} on {self.page_url}"
