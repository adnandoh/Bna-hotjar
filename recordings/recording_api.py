from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from recordings.models import Recording
from events.models import Session
from django.utils import timezone
import json

@api_view(['POST'])
@permission_classes([AllowAny])
def save_recording_events(request):
    """
    Save rrweb recording events for a session
    """
    session_id = request.data.get('session_id')
    events = request.data.get('events', [])
    
    if not session_id or not events:
        return Response({'error': 'session_id and events are required'}, status=400)
    
    try:
        session = Session.objects.get(id=session_id)
    except Session.DoesNotExist:
        return Response({'error': 'Session not found'}, status=404)
    
    # Get or create recording for this session
    recording, created = Recording.objects.get_or_create(
        session=session,
        defaults={
            'recording_id': f"rec_{session_id}",
            'duration': 0,
            'event_count': 0,
            'recording_data': []
        }
    )
    
    # Append new events to existing recording data
    existing_data = recording.recording_data or []
    existing_data.extend(events)
    recording.recording_data = existing_data
    recording.event_count = len(existing_data)
    
    # Update duration based on timestamps
    if existing_data:
        first_timestamp = existing_data[0].get('timestamp', 0)
        last_timestamp = existing_data[-1].get('timestamp', 0)
        recording.duration = int((last_timestamp - first_timestamp) / 1000)  # Convert to seconds
    
    # Check for errors and rage clicks in events
    has_errors = any(e.get('type') == 5 and 'error' in str(e.get('data', {})) for e in events)
    has_rage_clicks = any(e.get('type') == 5 and 'rage' in str(e.get('data', {})) for e in events)
    
    if has_errors:
        recording.has_errors = True
    if has_rage_clicks:
        recording.has_rage_clicks = True
    
    recording.save()
    
    return Response({
        'success': True,
        'recording_id': recording.recording_id,
        'event_count': recording.event_count
    })


@api_view(['GET'])
def get_recording_data(request, recording_id):
    """
    Get recording data for playback
    """
    try:
        recording = Recording.objects.get(recording_id=recording_id)
    except Recording.DoesNotExist:
        return Response({'error': 'Recording not found'}, status=404)
    
    return Response({
        'recording_id': recording.recording_id,
        'session_id': recording.session.id,
        'duration': recording.duration,
        'event_count': recording.event_count,
        'events': recording.recording_data,
        'has_errors': recording.has_errors,
        'has_rage_clicks': recording.has_rage_clicks,
        'created_at': recording.created_at.isoformat()
    })
