from rest_framework import serializers
from .models import HeatmapData

class HeatmapDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeatmapData
        fields = '__all__'
