from rest_framework import serializers
from .models import FormAnalytics

class FormAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormAnalytics
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
