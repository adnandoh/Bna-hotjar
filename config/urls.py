"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/sites/', include('sites.urls')),
    path('api/track/', include('events.urls')),
    path('api/recordings/', include('recordings.urls')),
    path('api/heatmaps/', include('heatmaps.urls')),
    path('api/funnels/', include('funnels.urls')),
    path('api/forms/', include('forms.urls')),
    path('api/surveys/', include('surveys.urls')),
    path('api/teams/', include('teams.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
