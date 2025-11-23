from rest_framework.routers import DefaultRouter
from .views import FunnelViewSet

router = DefaultRouter()
router.register(r'', FunnelViewSet, basename='funnel')

urlpatterns = router.urls
