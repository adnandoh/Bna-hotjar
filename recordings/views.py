from rest_framework import viewsets, permissions
from .models import Recording
from .serializers import RecordingSerializer

class RecordingViewSet(viewsets.ModelViewSet):
    serializer_class = RecordingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter recordings by sites owned by the user
        return Recording.objects.filter(session__site__owner=self.request.user)
