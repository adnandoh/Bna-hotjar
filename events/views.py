from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.utils import timezone
from .models import Session, Event
from .serializers import SessionSerializer, EventSerializer

class SessionViewSet(viewsets.ModelViewSet):
    serializer_class = SessionSerializer
    permission_classes = [permissions.AllowAny] # Allow tracking script to create sessions

    def get_queryset(self):
        # Only allow authenticated users to list sessions for their sites
        if self.request.user.is_authenticated:
            return Session.objects.filter(site__owner=self.request.user)
        return Session.objects.none()
    
    def perform_create(self, serializer):
        """Update site's last_activity_at when a new session is created"""
        session = serializer.save()
        site = session.site
        site.is_connected = True
        site.last_activity_at = timezone.now()
        site.save(update_fields=['is_connected', 'last_activity_at'])

class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Update site's last_activity_at when events are received
        if is_many and serializer.data:
            # Get the first event's session to find the site
            first_event = Event.objects.filter(id=serializer.data[0]['id']).select_related('session__site').first()
            if first_event and first_event.session:
                site = first_event.session.site
                site.is_connected = True
                site.last_activity_at = timezone.now()
                site.save(update_fields=['is_connected', 'last_activity_at'])
        elif not is_many and serializer.data:
            event = Event.objects.filter(id=serializer.data['id']).select_related('session__site').first()
            if event and event.session:
                site = event.session.site
                site.is_connected = True
                site.last_activity_at = timezone.now()
                site.save(update_fields=['is_connected', 'last_activity_at'])
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
