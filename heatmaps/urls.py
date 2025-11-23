from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import HeatmapDataViewSet
from .api_views import trigger_heatmap_generation, get_tracking_script
from .heatmap_views import get_heatmap_data, get_page_screenshot

router = DefaultRouter()
router.register(r'', HeatmapDataViewSet, basename='heatmap')

urlpatterns = [
    path('generate/<int:site_id>/', trigger_heatmap_generation, name='generate_heatmap'),
    path('tracking-script/<int:site_id>/', get_tracking_script, name='tracking_script'),
    path('data/<int:site_id>/', get_heatmap_data, name='heatmap_data'),
    path('screenshot/<int:site_id>/', get_page_screenshot, name='page_screenshot'),
] + router.urls
