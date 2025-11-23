from rest_framework import viewsets, permissions
from .models import FormAnalytics
from .serializers import FormAnalyticsSerializer

class FormAnalyticsViewSet(viewsets.ModelViewSet):
    serializer_class = FormAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FormAnalytics.objects.filter(site__owner=self.request.user)
