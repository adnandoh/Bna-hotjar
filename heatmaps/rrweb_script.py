"""
Enhanced tracking script with rrweb DOM recording
This should be served from a CDN in production
"""

RRWEB_TRACKING_SCRIPT = """
<!-- Load rrweb from CDN -->
<script src="https://cdn.jsdelivr.net/npm/rrweb@latest/dist/rrweb.min.js"></script>
<script>
(function() {
    'use strict';
    
    const BATCH_INTERVAL = 5000;
    const API_BASE = 'http://localhost:8000/api/track';
    
    class HotjarClone {
        constructor(siteId, config = {}) {
            this.siteId = siteId;
            this.config = {
                samplingRate: config.samplingRate || 1.0,
                recordDOM: config.recordDOM !== false,
                ...config
            };
            this.sessionId = null;
            this.eventQueue = [];
            this.rrwebEvents = [];
            this.stopRecording = null;
            
            if (Math.random() > this.config.samplingRate) {
                console.log('Session not sampled');
                return;
            }
            
            this.init();
        }

        async init() {
            await this.createSession();
            if (this.sessionId) {
                if (this.config.recordDOM && window.rrweb) {
                    this.startDOMRecording();
                }
                this.startBatchSender();
                this.setupSurveys();
            }
        }

        async createSession() {
            try {
                const response = await fetch(`${API_BASE}/sessions/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        tracking_id: this.siteId,
                        device_type: this.getDeviceType(),
                        browser: navigator.userAgent,
                        os: navigator.platform,
                        viewport: {
                            width: window.innerWidth,
                            height: window.innerHeight
                        }
                    })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    this.sessionId = data.id;
                    console.log('Tracking initialized with session:', this.sessionId);
                }
            } catch (e) {
                console.error('Tracking init failed:', e);
            }
        }

        getDeviceType() {
            const ua = navigator.userAgent;
            if (/Mobile|Android|iPhone/i.test(ua)) return 'mobile';
            if (/Tablet|iPad/i.test(ua)) return 'tablet';
            return 'desktop';
        }

        startDOMRecording() {
            if (!window.rrweb) {
                console.error('rrweb not loaded');
                return;
            }

            this.stopRecording = window.rrweb.record({
                emit: (event) => {
                    this.rrwebEvents.push(event);
                },
                checkoutEveryNms: 30000, // Create new snapshot every 30 seconds
                sampling: {
                    mousemove: true,
                    mouseInteraction: true,
                    scroll: 150,
                    input: 'last'
                }
            });

            console.log('DOM recording started');
        }

        startBatchSender() {
            setInterval(() => {
                if (this.rrwebEvents.length > 0) {
                    this.sendRecordingData();
                }
            }, BATCH_INTERVAL);
        }

        async sendRecordingData() {
            if (this.rrwebEvents.length === 0) return;
            
            const events = this.rrwebEvents.splice(0);
            
            try {
                await fetch(`${API_BASE}/recording-events/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: this.sessionId,
                        events: events
                    }),
                    keepalive: true
                });
            } catch (err) {
                console.error('Failed to send recording data:', err);
                // Re-add events if failed
                this.rrwebEvents.unshift(...events);
            }
        }

        async setupSurveys() {
            try {
                const response = await fetch(`http://localhost:8000/api/surveys/active/${this.siteId}/?page_url=${encodeURIComponent(window.location.pathname)}`);
                if (response.ok) {
                    const data = await response.json();
                    data.surveys.forEach(survey => this.initializeSurvey(survey));
                }
            } catch (e) {
                console.error('Failed to load surveys:', e);
            }
        }

        initializeSurvey(survey) {
            const triggerConfig = survey.trigger_config || {};
            
            switch (survey.trigger_type) {
                case 'page_load':
                    const delay = triggerConfig.delay || 0;
                    setTimeout(() => this.showSurvey(survey), delay * 1000);
                    break;
                case 'exit_intent':
                    this.setupExitIntent(survey);
                    break;
                case 'time_delay':
                    const timeDelay = triggerConfig.seconds || 10;
                    setTimeout(() => this.showSurvey(survey), timeDelay * 1000);
                    break;
                case 'scroll':
                    this.setupScrollTrigger(survey, triggerConfig.percentage || 50);
                    break;
            }
        }

        setupExitIntent(survey) {
            let shown = false;
            document.addEventListener('mouseleave', (e) => {
                if (!shown && e.clientY <= 0) {
                    this.showSurvey(survey);
                    shown = true;
                }
            });
        }

        setupScrollTrigger(survey, targetPercentage) {
            let shown = false;
            const checkScroll = () => {
                if (shown) return;
                const scrollPercentage = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
                if (scrollPercentage >= targetPercentage) {
                    this.showSurvey(survey);
                    shown = true;
                    window.removeEventListener('scroll', checkScroll);
                }
            };
            window.addEventListener('scroll', checkScroll);
        }

        showSurvey(survey) {
            const modal = document.createElement('div');
            modal.id = `hotjar-survey-${survey.id}`;
            modal.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);display:flex;align-items:center;justify-content:center;z-index:999999;';

            const content = document.createElement('div');
            content.style.cssText = 'background:white;padding:30px;border-radius:12px;max-width:500px;width:90%;max-height:80vh;overflow-y:auto;box-shadow:0 20px 60px rgba(0,0,0,0.3);';

            let html = `<h2 style="margin:0 0 20px 0;font-size:24px;color:#333;">${survey.name}</h2>`;
            
            survey.questions.forEach((q, index) => {
                html += `<div style="margin-bottom:20px;">`;
                html += `<label style="display:block;margin-bottom:8px;font-weight:500;color:#555;">${q.question}</label>`;
                
                switch (q.type) {
                    case 'text':
                        html += `<textarea id="q${index}" style="width:100%;padding:10px;border:1px solid #ddd;border-radius:6px;font-family:inherit;" rows="3"></textarea>`;
                        break;
                    case 'rating':
                        html += `<div style="display:flex;gap:10px;">`;
                        for (let i = 1; i <= 5; i++) {
                            html += `<button type="button" class="rating-btn" data-question="${index}" data-value="${i}" style="padding:10px 15px;border:2px solid #ddd;border-radius:6px;background:white;cursor:pointer;font-weight:500;">${i}</button>`;
                        }
                        html += `</div>`;
                        break;
                    case 'yes_no':
                        html += `<div style="display:flex;gap:10px;">`;
                        html += `<button type="button" class="yesno-btn" data-question="${index}" data-value="yes" style="flex:1;padding:10px;border:2px solid #ddd;border-radius:6px;background:white;cursor:pointer;font-weight:500;">Yes</button>`;
                        html += `<button type="button" class="yesno-btn" data-question="${index}" data-value="no" style="flex:1;padding:10px;border:2px solid #ddd;border-radius:6px;background:white;cursor:pointer;font-weight:500;">No</button>`;
                        html += `</div>`;
                        break;
                    case 'nps':
                        html += `<div style="display:flex;gap:5px;flex-wrap:wrap;">`;
                        for (let i = 0; i <= 10; i++) {
                            html += `<button type="button" class="nps-btn" data-question="${index}" data-value="${i}" style="padding:10px;border:2px solid #ddd;border-radius:6px;background:white;cursor:pointer;min-width:40px;font-weight:500;">${i}</button>`;
                        }
                        html += `</div>`;
                        break;
                }
                html += `</div>`;
            });

            html += `<div style="display:flex;gap:10px;margin-top:30px;"><button id="survey-submit" style="flex:1;padding:12px;background:#6366f1;color:white;border:none;border-radius:6px;font-weight:600;cursor:pointer;">Submit</button><button id="survey-close" style="padding:12px 20px;background:#f3f4f6;color:#666;border:none;border-radius:6px;font-weight:600;cursor:pointer;">Close</button></div>`;

            content.innerHTML = html;
            modal.appendChild(content);
            document.body.appendChild(modal);

            const responses = {};
            
            content.querySelectorAll('.rating-btn, .yesno-btn, .nps-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    const question = this.getAttribute('data-question');
                    const value = this.getAttribute('data-value');
                    responses[question] = value;
                    this.parentElement.querySelectorAll('button').forEach(b => {
                        b.style.background = 'white';
                        b.style.borderColor = '#ddd';
                        b.style.color = '#333';
                    });
                    this.style.background = '#6366f1';
                    this.style.borderColor = '#6366f1';
                    this.style.color = 'white';
                });
            });

            content.querySelector('#survey-submit').addEventListener('click', () => {
                survey.questions.forEach((q, index) => {
                    if (q.type === 'text') {
                        const textarea = content.querySelector(`#q${index}`);
                        if (textarea) responses[index] = textarea.value;
                    }
                });
                this.submitSurvey(survey.id, responses);
                document.body.removeChild(modal);
            });

            content.querySelector('#survey-close').addEventListener('click', () => {
                document.body.removeChild(modal);
            });
        }

        async submitSurvey(surveyId, responses) {
            try {
                await fetch('http://localhost:8000/api/surveys/submit/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        survey_id: surveyId,
                        session_id: this.sessionId,
                        responses: responses
                    })
                });
            } catch (e) {
                console.error('Failed to submit survey:', e);
            }
        }

        // Public API
        trackEvent(eventName, properties = {}) {
            this.rrwebEvents.push({
                type: 5, // Custom event type in rrweb
                data: {
                    tag: 'custom',
                    payload: { eventName, properties }
                },
                timestamp: Date.now()
            });
        }

        identify(userId, traits = {}) {
            if (!this.sessionId) return;
            fetch(`${API_BASE}/identify/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    user_identifier: userId,
                    traits: traits
                })
            }).catch(err => console.error('Identify failed:', err));
        }

        tagSession(tags) {
            if (!this.sessionId) return;
            fetch(`${API_BASE}/identify/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    user_identifier: null,
                    traits: { tags: tags }
                })
            }).catch(err => console.error('Tag session failed:', err));
        }
    }

    // Auto-initialize
    const scriptTag = document.currentScript;
    if (scriptTag) {
        const src = scriptTag.src;
        const url = new URL(src);
        const siteId = url.searchParams.get('id');
        const samplingRate = parseFloat(url.searchParams.get('sampling') || '1.0');
        
        if (siteId) {
            window.HotjarClone = new HotjarClone(siteId, { samplingRate });
        }
    }

    if (!window.HotjarClone) {
        window.HotjarClone = HotjarClone;
    }
})();
</script>
"""
