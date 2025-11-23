from rest_framework import serializers
from .models import Session, Event

from sites.models import Site

class SessionSerializer(serializers.ModelSerializer):
    tracking_id = serializers.UUIDField(write_only=True)
    site = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Session
        fields = '__all__'

    def create(self, validated_data):
        tracking_id = validated_data.pop('tracking_id')
        try:
            site = Site.objects.get(tracking_id=tracking_id)
        except Site.DoesNotExist:
            raise serializers.ValidationError("Invalid tracking ID")
        session = Session.objects.create(site=site, **validated_data)
        return session

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
