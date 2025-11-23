from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import SessionViewSet, EventViewSet
from .api_views import identify_user
from recordings.recording_api import save_recording_events

router = DefaultRouter()
router.register(r'sessions', SessionViewSet, basename='session')
router.register(r'events', EventViewSet, basename='event')

urlpatterns = [
    path('identify/', identify_user, name='identify_user'),
    path('recording-events/', save_recording_events, name='recording_events'),
] + router.urls
