from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from events.models import Session, Event

@api_view(['POST'])
@permission_classes([AllowAny])
def identify_user(request):
    """
    Identify a user and associate them with a session
    """
    session_id = request.data.get('session_id')
    user_identifier = request.data.get('user_identifier')
    traits = request.data.get('traits', {})
    
    try:
        session = Session.objects.get(session_id=session_id)
        session.user_identifier = user_identifier
        session.tags = traits
        session.save()
        
        return Response({'status': 'success', 'message': 'User identified'})
    except Session.DoesNotExist:
        return Response({'status': 'error', 'message': 'Session not found'}, status=404)
