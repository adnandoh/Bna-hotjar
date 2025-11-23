from django.urls import path
from .views import dashboard_stats, funnel_analytics

urlpatterns = [
    path('dashboard/', dashboard_stats, name='dashboard_stats'),
    path('funnels/<int:funnel_id>/', funnel_analytics, name='funnel_analytics'),
]
