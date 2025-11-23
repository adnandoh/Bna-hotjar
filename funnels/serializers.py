from rest_framework import serializers
from .models import Funnel

class FunnelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Funnel
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
