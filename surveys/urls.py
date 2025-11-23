from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import SurveyViewSet, SurveyResponseViewSet
from .api_views import get_active_surveys, submit_survey_response

router = DefaultRouter()
router.register(r'surveys', SurveyViewSet, basename='survey')
router.register(r'responses', SurveyResponseViewSet, basename='survey-response')

urlpatterns = [
    path('active/<int:site_id>/', get_active_surveys, name='active_surveys'),
    path('submit/', submit_survey_response, name='submit_survey'),
] + router.urls
