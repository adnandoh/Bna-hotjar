from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse
from analytics.tasks import generate_heatmap_data

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_heatmap_generation(request, site_id):
    """
    Trigger background task to generate heatmap
    """
    page_url = request.data.get('page_url')
    heatmap_type = request.data.get('heatmap_type', 'click')
    device_type = request.data.get('device_type', 'desktop')
    days = request.data.get('days', 7)
    
    # Trigger task synchronously (Celery removed)
    # task = generate_heatmap_data.delay(site_id, page_url, heatmap_type, device_type, days)
    result = generate_heatmap_data(site_id, page_url, heatmap_type, device_type, days)
    
    return Response({
        'status': 'success',
        'message': 'Heatmap generation completed',
        'result': result
    })


def get_tracking_script(request, site_id):
    """
    Generate tracking script for a specific site
    """
    from sites.models import Site
    from rest_framework_simplejwt.authentication import JWTAuthentication
    from rest_framework.exceptions import AuthenticationFailed
    
    # Manual JWT authentication
    jwt_auth = JWTAuthentication()
    try:
        # Extract and validate JWT token
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return HttpResponse('// Unauthorized - No token provided', content_type='application/javascript', status=401)
        
        # Validate token and get user
        validated_token = jwt_auth.get_validated_token(auth_header.split(' ')[1])
        user = jwt_auth.get_user(validated_token)
        
        if not user or not user.is_authenticated:
            return HttpResponse('// Unauthorized - Invalid token', content_type='application/javascript', status=401)
            
    except (AuthenticationFailed, Exception) as e:
        return HttpResponse(f'// Unauthorized - {str(e)}', content_type='application/javascript', status=401)
    
    try:
        site = Site.objects.get(id=site_id, owner=user)
        
        api_base = request.build_absolute_uri('/api/track')
        
        script = f"""
(function() {{
    'use strict';
    const BATCH_INTERVAL = 5000;
    const MOUSE_MOVE_THROTTLE = 100;
    const API_BASE = '{api_base}';
    const TRACKING_ID = '{site.tracking_id}';

    class HotjarClone {{
        constructor(trackingId) {{
            this.trackingId = trackingId;
            this.sessionId = null;
            this.eventQueue = [];
            this.init();
        }}

        async init() {{
            await this.createSession();
            if (this.sessionId) {{
                this.setupEventListeners();
                this.startBatchSender();
            }}
        }}
        
        async createSession() {{
            try {{
                const response = await fetch(`${{API_BASE}}/sessions/`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        tracking_id: this.trackingId,
                        device_type: /Mobile|Android|iPhone/i.test(navigator.userAgent) ? 'mobile' : 'desktop',
                        browser: navigator.userAgent,
                        os: navigator.platform,
                        viewport: {{ width: window.innerWidth, height: window.innerHeight }}
                    }})
                }});
                if (response.ok) {{
                    const data = await response.json();
                    this.sessionId = data.id;
                    console.log('Tracking initialized');
                }}
            }} catch (e) {{
                console.error('Tracking init failed:', e);
            }}
        }}

        setupEventListeners() {{
            document.addEventListener('click', (e) => this.trackClick(e));
            
            let lastMouseMove = 0;
            document.addEventListener('mousemove', (e) => {{
                const now = Date.now();
                if (now - lastMouseMove > MOUSE_MOVE_THROTTLE) {{
                    this.trackMouseMove(e);
                    lastMouseMove = now;
                }}
            }});
            
            let scrollTimeout;
            window.addEventListener('scroll', () => {{
                clearTimeout(scrollTimeout);
                scrollTimeout = setTimeout(() => this.trackScroll(), 100);
            }});
        }}

        trackClick(event) {{
            this.queueEvent({{
                event_type: 'click',
                timestamp: new Date().toISOString(),
                session: this.sessionId,
                page_url: window.location.href,
                data: {{
                    x: event.clientX,
                    y: event.clientY,
                    target: event.target.tagName,
                    id: event.target.id,
                    classes: Array.from(event.target.classList)
                }}
            }});
        }}

        trackMouseMove(event) {{
            this.queueEvent({{
                event_type: 'mouse_move',
                timestamp: new Date().toISOString(),
                session: this.sessionId,
                page_url: window.location.href,
                data: {{ x: event.clientX, y: event.clientY }}
            }});
        }}

        trackScroll() {{
            const scrollPercentage = Math.round(
                (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100
            );
            this.queueEvent({{
                event_type: 'scroll',
                timestamp: new Date().toISOString(),
                session: this.sessionId,
                page_url: window.location.href,
                data: {{ y: window.scrollY, percentage: scrollPercentage }}
            }});
        }}

        queueEvent(event) {{
            this.eventQueue.push(event);
        }}

        startBatchSender() {{
            setInterval(() => {{
                if (this.eventQueue.length > 0) {{
                    this.sendEvents();
                }}
            }}, BATCH_INTERVAL);
        }}

        sendEvents() {{
            const events = this.eventQueue.splice(0);
            fetch(`${{API_BASE}}/events/`, {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify(events),
                keepalive: true
            }}).catch(err => console.error('Failed to send events:', err));
        }}
    }}
    
    new HotjarClone(TRACKING_ID);
}})();
"""
        
        return HttpResponse(script, content_type='application/javascript')
    except Site.DoesNotExist:
        return HttpResponse('// Site not found', content_type='application/javascript', status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return HttpResponse(f'// Error generating script: {str(e)}', content_type='application/javascript', status=500)
