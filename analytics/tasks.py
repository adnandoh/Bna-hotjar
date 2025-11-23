from celery import shared_task
from django.db.models import Count
from events.models import Event
from heatmaps.models import HeatmapData
from datetime import datetime, timedelta

@shared_task
def generate_heatmap_data(site_id, page_url, heatmap_type='click', device_type='desktop', days=7):
    """
    Generate heatmap data by aggregating events
    """
    from sites.models import Site
    
    try:
        site = Site.objects.get(id=site_id)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Fetch events for the specified page and type
        events = Event.objects.filter(
            session__site=site,
            page_url=page_url,
            event_type=heatmap_type,
            timestamp__date__gte=start_date,
            timestamp__date__lte=end_date,
            session__device_type=device_type
        )
        
        # Aggregate coordinates
        heatmap_points = []
        for event in events:
            if 'x' in event.data and 'y' in event.data:
                heatmap_points.append({
                    'x': event.data['x'],
                    'y': event.data['y'],
                    'value': 1
                })
        
        # Aggregate duplicate points
        aggregated = {}
        for point in heatmap_points:
            key = f"{point['x']},{point['y']}"
            if key in aggregated:
                aggregated[key]['value'] += 1
            else:
                aggregated[key] = point
        
        heatmap_data = list(aggregated.values())
        
        # Save or update heatmap
        HeatmapData.objects.update_or_create(
            site=site,
            page_url=page_url,
            heatmap_type=heatmap_type,
            device_type=device_type,
            date_range_start=start_date,
            date_range_end=end_date,
            defaults={
                'data': heatmap_data,
                'session_count': Event.objects.filter(
                    session__site=site,
                    page_url=page_url,
                    timestamp__date__gte=start_date,
                    timestamp__date__lte=end_date
                ).values('session').distinct().count()
            }
        )
        
        return f"Heatmap generated for {page_url}"
    except Exception as e:
        return f"Error generating heatmap: {str(e)}"


@shared_task
def process_recording(session_id):
    """
    Process session events into a recording
    """
    from events.models import Session
    from recordings.models import Recording
    
    try:
        session = Session.objects.get(id=session_id)
        events = Event.objects.filter(session=session).order_by('timestamp')
        
        # Calculate duration
        if events.exists():
            first_event = events.first()
            last_event = events.last()
            duration = (last_event.timestamp - first_event.timestamp).total_seconds()
        else:
            duration = 0
        
        # Check for errors and rage clicks
        has_errors = events.filter(event_type='error').exists()
        has_rage_clicks = events.filter(event_type='rage_click').exists()
        
        # Create or update recording
        Recording.objects.update_or_create(
            session=session,
            defaults={
                'storage_url': f'recordings/{session.session_id}.json',  # Placeholder
                'duration': int(duration),
                'event_count': events.count(),
                'has_errors': has_errors,
                'has_rage_clicks': has_rage_clicks
            }
        )
        
        return f"Recording processed for session {session_id}"
    except Exception as e:
        return f"Error processing recording: {str(e)}"


@shared_task
def calculate_funnel_metrics(funnel_id):
    """
    Calculate conversion metrics for a funnel
    """
    from funnels.models import Funnel
    from events.models import Session, Event
    
    try:
        funnel = Funnel.objects.get(id=funnel_id)
        steps = funnel.steps
        
        # This is a simplified implementation
        # In production, you'd track sessions through each step
        
        metrics = {
            'total_sessions': Session.objects.filter(site=funnel.site).count(),
            'steps': []
        }
        
        for step in steps:
            step_sessions = Event.objects.filter(
                session__site=funnel.site,
                page_url=step.get('url', '')
            ).values('session').distinct().count()
            
            metrics['steps'].append({
                'name': step.get('name', ''),
                'sessions': step_sessions,
                'conversion_rate': (step_sessions / metrics['total_sessions'] * 100) if metrics['total_sessions'] > 0 else 0
            })
        
        return f"Funnel metrics calculated: {metrics}"
    except Exception as e:
        return f"Error calculating funnel metrics: {str(e)}"
