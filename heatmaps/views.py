from rest_framework import viewsets, permissions
from .models import HeatmapData
from .serializers import HeatmapDataSerializer

class HeatmapDataViewSet(viewsets.ModelViewSet):
    serializer_class = HeatmapDataSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return HeatmapData.objects.filter(site__owner=self.request.user)
