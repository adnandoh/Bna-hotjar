from rest_framework import viewsets, permissions
from .models import Funnel
from .serializers import FunnelSerializer

class FunnelViewSet(viewsets.ModelViewSet):
    serializer_class = FunnelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Funnel.objects.filter(site__owner=self.request.user)
