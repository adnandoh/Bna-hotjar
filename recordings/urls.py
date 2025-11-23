from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import RecordingViewSet
from .recording_api import save_recording_events, get_recording_data

router = DefaultRouter()
router.register(r'', RecordingViewSet, basename='recording')

urlpatterns = [
    path('data/<str:recording_id>/', get_recording_data, name='recording_data'),
] + router.urls
