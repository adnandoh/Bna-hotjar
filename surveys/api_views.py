from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from surveys.models import Survey
from django.utils import timezone

@api_view(['GET'])
@permission_classes([AllowAny])
def get_active_surveys(request, site_id):
    """
    Get active surveys for a site that should be triggered
    Returns surveys with their trigger configurations
    """
    page_url = request.GET.get('page_url', '/')
    
    # Get active surveys for this site
    surveys = Survey.objects.filter(
        site_id=site_id,
        is_active=True
    )
    
    # Filter by targeting rules if page_url is provided
    matching_surveys = []
    for survey in surveys:
        targeting_rules = survey.targeting_rules or {}
        
        # Check URL pattern matching
        url_patterns = targeting_rules.get('url_patterns', [])
        if url_patterns:
            if not any(pattern in page_url for pattern in url_patterns):
                continue
        
        # Prepare survey data for frontend
        survey_data = {
            'id': survey.id,
            'name': survey.name,
            'questions': survey.questions,
            'trigger_type': survey.trigger_type,
            'trigger_config': survey.trigger_config or {},
            'targeting_rules': targeting_rules
        }
        
        matching_surveys.append(survey_data)
    
    return Response({
        'surveys': matching_surveys,
        'count': len(matching_surveys)
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def submit_survey_response(request):
    """
    Submit a survey response from the tracking script
    """
    from surveys.models import SurveyResponse
    
    survey_id = request.data.get('survey_id')
    session_id = request.data.get('session_id')
    responses = request.data.get('responses', {})
    
    if not survey_id:
        return Response({'error': 'survey_id is required'}, status=400)
    
    try:
        survey = Survey.objects.get(id=survey_id)
    except Survey.DoesNotExist:
        return Response({'error': 'Survey not found'}, status=404)
    
    # Create survey response
    survey_response = SurveyResponse.objects.create(
        survey=survey,
        session_id=session_id,
        responses=responses,
        submitted_at=timezone.now()
    )
    
    return Response({
        'success': True,
        'response_id': survey_response.id
    }, status=201)
