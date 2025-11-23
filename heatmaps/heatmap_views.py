from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count
from events.models import Event
from heatmaps.models import HeatmapData
from sites.models import Site
from datetime import datetime, timedelta

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_heatmap_data(request, site_id):
    """
    Get aggregated heatmap data for a specific site and page
    """
    try:
        site = Site.objects.get(id=site_id, owner=request.user)
    except Site.DoesNotExist:
        return Response({'error': 'Site not found'}, status=404)
    
    # Get query parameters
    page_url = request.GET.get('page_url', '/')
    heatmap_type = request.GET.get('type', 'click')  # click, scroll, move
    device_type = request.GET.get('device', 'desktop')
    days = int(request.GET.get('days', 7))
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Map heatmap type to event type
    event_type_map = {
        'click': 'click',
        'scroll': 'scroll',
        'move': 'mouse_move'
    }
    event_type = event_type_map.get(heatmap_type, 'click')
    
    # Fetch events
    events = Event.objects.filter(
        session__site=site,
        page_url__icontains=page_url,
        event_type=event_type,
        timestamp__gte=start_date,
        timestamp__lte=end_date,
        session__device_type=device_type
    )
    
    # Aggregate coordinates
    heatmap_points = []
    max_value = 0
    
    if event_type in ['click', 'mouse_move']:
        # For click and move events, aggregate by coordinates
        coordinate_counts = {}
        
        for event in events:
            if 'x' in event.data and 'y' in event.data:
                x = int(event.data['x'])
                y = int(event.data['y'])
                
                # Round to nearest 10 pixels for better aggregation
                x = round(x / 10) * 10
                y = round(y / 10) * 10
                
                key = f"{x},{y}"
                coordinate_counts[key] = coordinate_counts.get(key, 0) + 1
                max_value = max(max_value, coordinate_counts[key])
        
        # Convert to heatmap format
        for key, count in coordinate_counts.items():
            x, y = map(int, key.split(','))
            heatmap_points.append({
                'x': x,
                'y': y,
                'value': count
            })
    
    elif event_type == 'scroll':
        # For scroll events, create scroll depth heatmap
        scroll_depths = {}
        
        for event in events:
            if 'y' in event.data:
                y = int(event.data['y'])
                # Round to nearest 50 pixels
                y = round(y / 50) * 50
                scroll_depths[y] = scroll_depths.get(y, 0) + 1
                max_value = max(max_value, scroll_depths[y])
        
        # Convert to heatmap format (full width bars)
        for y, count in scroll_depths.items():
            heatmap_points.append({
                'x': 0,
                'y': y,
                'value': count,
                'width': 1920  # Full width indicator
            })
    
    # Get session count
    session_count = events.values('session').distinct().count()
    
    # Get available pages for this site
    available_pages = Event.objects.filter(
        session__site=site,
        event_type='page_view'
    ).values_list('page_url', flat=True).distinct()[:20]
    
    return Response({
        'site_id': site_id,
        'page_url': page_url,
        'heatmap_type': heatmap_type,
        'device_type': device_type,
        'date_range': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat(),
            'days': days
        },
        'data': heatmap_points,
        'max': max_value,
        'session_count': session_count,
        'total_events': events.count(),
        'available_pages': list(available_pages)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_page_screenshot(request, site_id):
    """
    Get or generate a screenshot for a page (placeholder for now)
    In production, this would use a service like Puppeteer
    """
    page_url = request.GET.get('page_url', '/')
    
    return Response({
        'screenshot_url': None,  # Would be S3 URL in production
        'width': 1920,
        'height': 1080,
        'message': 'Screenshot generation not implemented. Heatmap will overlay on live page.'
    })
