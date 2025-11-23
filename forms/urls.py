from rest_framework.routers import DefaultRouter
from .views import FormAnalyticsViewSet

router = DefaultRouter()
router.register(r'', FormAnalyticsViewSet, basename='form')

urlpatterns = router.urls
