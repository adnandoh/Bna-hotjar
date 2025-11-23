from django.db import models
from sites.models import Site

class HeatmapData(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    page_url = models.TextField()
    heatmap_type = models.CharField(max_length=50) # click, scroll, move
    device_type = models.CharField(max_length=50)
    date_range_start = models.DateField()
    date_range_end = models.DateField()
    data = models.JSONField() # Aggregated heatmap coordinates
    session_count = models.IntegerField()
    generated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [
            'site', 'page_url', 'heatmap_type', 
            'device_type', 'date_range_start', 'date_range_end'
        ]

    def __str__(self):
        return f"{self.heatmap_type} Heatmap for {self.page_url}"
