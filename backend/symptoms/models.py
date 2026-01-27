# ==================== symptoms/models.py ====================
from django.db import models
from users.models import User

class SymptomCategory(models.Model):
    """Categories of symptoms"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Symptom Categories'
        ordering = ['name']


class SymptomCheck(models.Model):
    """AI symptom checker results"""
    URGENCY_CHOICES = (
        ('emergency', 'Emergency'),
        ('doctor_visit', 'Doctor Visit'),
        ('home_care', 'Home Care'),
    )
    
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='symptom_checks', blank=True, null=True)
    
    # Input
    symptoms_description = models.TextField()
    
    # AI Analysis
    urgency_level = models.CharField(max_length=20, choices=URGENCY_CHOICES)
    recommendation = models.TextField()
    recommended_provider_type = models.CharField(max_length=100)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    # Detected conditions
    possible_conditions = models.TextField(blank=True, help_text="JSON array of possible conditions")
    
    # Follow-up
    follow_up_needed = models.BooleanField(default=True)
    appointment_booked = models.BooleanField(default=False)
    
    # Session info
    session_id = models.CharField(max_length=100, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        user_str = self.patient.get_full_name() if self.patient else 'Anonymous'
        return f"Symptom check by {user_str} - {self.urgency_level}"
    
    class Meta:
        ordering = ['-created_at']


class HealthTip(models.Model):
    """Health tips and educational content"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.ForeignKey(SymptomCategory, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']