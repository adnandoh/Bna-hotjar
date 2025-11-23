from rest_framework import viewsets, permissions
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

class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
