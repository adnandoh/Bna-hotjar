from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Avg, F
from events.models import Session, Event
from recordings.models import Recording
from datetime import datetime, timedelta

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Get comprehensive dashboard statistics
    """
    # Get date range from query params (default to last 7 days)
    days = int(request.GET.get('days', 7))
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Get user's sites
    from sites.models import Site
    user_sites = Site.objects.filter(owner=request.user)
    
    # Total sessions
    total_sessions = Session.objects.filter(
        site__in=user_sites,
        started_at__gte=start_date
    ).count()
    
    # Active users (unique user_identifiers)
    active_users = Session.objects.filter(
        site__in=user_sites,
        started_at__gte=start_date,
        user_identifier__isnull=False
    ).values('user_identifier').distinct().count()
    
    # Total recordings
    total_recordings = Recording.objects.filter(
        session__site__in=user_sites,
        created_at__gte=start_date
    ).count()
    
    # Average session duration
    avg_duration = Recording.objects.filter(
        session__site__in=user_sites,
        created_at__gte=start_date
    ).aggregate(avg=Avg('duration'))['avg'] or 0
    
    # Top pages by session count
    top_pages = Event.objects.filter(
        session__site__in=user_sites,
        timestamp__gte=start_date,
        event_type='page_view'
    ).values('page_url').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Recent recordings
    recent_recordings = Recording.objects.filter(
        session__site__in=user_sites
    ).select_related('session').order_by('-created_at')[:10]
    
    recent_recordings_data = [{
        'id': r.recording_id,
        'user': r.session.user_identifier or 'Anonymous',
        'duration': f"{r.duration // 60}m {r.duration % 60}s",
        'page': Event.objects.filter(session=r.session, event_type='page_view').first().page_url if Event.objects.filter(session=r.session, event_type='page_view').exists() else '/',
        'timestamp': r.created_at.isoformat()
    } for r in recent_recordings]
    
    # Sessions trend (daily breakdown)
    sessions_trend = []
    for i in range(days):
        day = start_date + timedelta(days=i)
        day_end = day + timedelta(days=1)
        count = Session.objects.filter(
            site__in=user_sites,
            started_at__gte=day,
            started_at__lt=day_end
        ).count()
        sessions_trend.append({
            'date': day.strftime('%Y-%m-%d'),
            'count': count
        })
    
    return Response({
        'total_sessions': total_sessions,
        'active_users': active_users,
        'total_recordings': total_recordings,
        'avg_session_duration': int(avg_duration),
        'top_pages': list(top_pages),
        'recent_recordings': recent_recordings_data,
        'sessions_trend': sessions_trend,
        'date_range': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat(),
            'days': days
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def funnel_analytics(request, funnel_id):
    """
    Get detailed analytics for a specific funnel
    """
    from funnels.models import Funnel
    
    try:
        funnel = Funnel.objects.get(id=funnel_id, site__owner=request.user)
    except Funnel.DoesNotExist:
        return Response({'error': 'Funnel not found'}, status=404)
    
    steps = funnel.steps
    analytics = []
    
    # Get all sessions for this site
    all_sessions = Session.objects.filter(site=funnel.site)
    total_sessions = all_sessions.count()
    
    previous_step_sessions = set(all_sessions.values_list('id', flat=True))
    
    for index, step in enumerate(steps):
        # Find sessions that reached this step
        step_events = Event.objects.filter(
            session__in=previous_step_sessions,
            page_url__icontains=step.get('url', '')
        ).values_list('session_id', flat=True).distinct()
        
        step_sessions = set(step_events)
        step_count = len(step_sessions)
        
        # Calculate conversion rate
        if index == 0:
            conversion_rate = 100.0
        else:
            conversion_rate = (step_count / len(previous_step_sessions) * 100) if previous_step_sessions else 0
        
        # Calculate drop-off
        drop_off_count = len(previous_step_sessions) - step_count
        drop_off_rate = (drop_off_count / len(previous_step_sessions) * 100) if previous_step_sessions else 0
        
        analytics.append({
            'step_number': index + 1,
            'step_name': step.get('name', ''),
            'step_url': step.get('url', ''),
            'sessions': step_count,
            'conversion_rate': round(conversion_rate, 2),
            'drop_off_count': drop_off_count,
            'drop_off_rate': round(drop_off_rate, 2),
            'overall_conversion': round((step_count / total_sessions * 100) if total_sessions else 0, 2)
        })
        
        previous_step_sessions = step_sessions
    
    return Response({
        'funnel_id': funnel_id,
        'funnel_name': funnel.name,
        'total_sessions': total_sessions,
        'steps': analytics,
        'overall_conversion': analytics[-1]['overall_conversion'] if analytics else 0
    })
