from rest_framework import serializers
from .models import Site

class SiteSerializer(serializers.ModelSerializer):
    connection_status = serializers.ReadOnlyField()
    
    class Meta:
        model = Site
        fields = '__all__'
        read_only_fields = ('owner', 'tracking_id', 'created_at', 'is_connected', 'last_activity_at')
