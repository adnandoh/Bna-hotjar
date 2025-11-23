from rest_framework import serializers
from .models import Recording
from events.serializers import SessionSerializer

class RecordingSerializer(serializers.ModelSerializer):
    session = SessionSerializer(read_only=True)
    
    class Meta:
        model = Recording
        fields = '__all__'
