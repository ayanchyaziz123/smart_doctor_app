# ==================== symptoms/admin.py ====================
from django.contrib import admin
from .models import SymptomCategory, SymptomCheck, HealthTip

@admin.register(SymptomCategory)\

class SymptomCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(SymptomCheck)
class SymptomCheckAdmin(admin.ModelAdmin):
    list_display = ('get_patient', 'urgency_level', 'recommended_provider_type', 'appointment_booked', 'created_at')
    list_filter = ('urgency_level', 'appointment_booked', 'follow_up_needed', 'created_at')
    search_fields = ('symptoms_description', 'patient__username')
    readonly_fields = ('created_at',)
    
    def get_patient(self, obj):
        return obj.patient.get_full_name() if obj.patient else 'Anonymous'
    get_patient.short_description = 'Patient'
    
    fieldsets = (
        ('Patient', {
            'fields': ('patient', 'session_id', 'ip_address')
        }),
        ('Symptoms', {
            'fields': ('symptoms_description',)
        }),
        ('AI Analysis', {
            'fields': ('urgency_level', 'recommendation', 'recommended_provider_type', 'confidence_score', 'possible_conditions')
        }),
        ('Follow-up', {
            'fields': ('follow_up_needed', 'appointment_booked')
        }),
    )


@admin.register(HealthTip)
class HealthTipAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_active', 'created_at')
    list_filter = ('is_active', 'category', 'created_at')
    search_fields = ('title', 'content')