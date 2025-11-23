from rest_framework import viewsets, permissions
from .models import Survey, SurveyResponse
from .serializers import SurveySerializer, SurveyResponseSerializer

class SurveyViewSet(viewsets.ModelViewSet):
    serializer_class = SurveySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Survey.objects.filter(site__owner=self.request.user)


class SurveyResponseViewSet(viewsets.ModelViewSet):
    serializer_class = SurveyResponseSerializer
    permission_classes = [permissions.AllowAny]  # Allow public to submit responses

    def get_queryset(self):
        # Only authenticated users can list responses for their surveys
        if self.request.user.is_authenticated:
            return SurveyResponse.objects.filter(survey__site__owner=self.request.user)
        return SurveyResponse.objects.none()
