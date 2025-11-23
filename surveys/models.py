from django.db import models
from sites.models import Site

class Survey(models.Model):
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('rating', 'Rating Scale'),
        ('text', 'Open Text'),
        ('yes_no', 'Yes/No'),
        ('nps', 'Net Promoter Score'),
    ]
    
    TRIGGER_TYPES = [
        ('page_load', 'On Page Load'),
        ('exit_intent', 'On Exit Intent'),
        ('time_delay', 'After Time Delay'),
        ('scroll', 'On Scroll Percentage'),
        ('custom', 'Custom JavaScript Trigger'),
    ]

    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    questions = models.JSONField()  # List of questions with type and options
    trigger_type = models.CharField(max_length=50, choices=TRIGGER_TYPES)
    trigger_config = models.JSONField(default=dict)  # Config for trigger (delay, scroll %, etc.)
    targeting_rules = models.JSONField(default=dict)  # URL patterns, device type, etc.
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class SurveyResponse(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    session_id = models.CharField(max_length=255, null=True, blank=True)
    answers = models.JSONField()  # User's answers to questions
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response to {self.survey.name} at {self.submitted_at}"
