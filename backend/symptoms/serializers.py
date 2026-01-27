# ==================== symptoms/serializers.py ====================
from rest_framework import serializers
from .models import SymptomCategory, SymptomCheck, HealthTip
from users.serializers import UserProfileSerializer
import json


class SymptomCategorySerializer(serializers.ModelSerializer):
    """Serializer for SymptomCategory model"""
    class Meta:
        model = SymptomCategory
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']


class SymptomCheckSerializer(serializers.ModelSerializer):
    """Main serializer for SymptomCheck model"""
    patient_info = UserProfileSerializer(source='patient', read_only=True)
    urgency_display = serializers.CharField(source='get_urgency_level_display', read_only=True)
    possible_conditions_list = serializers.SerializerMethodField()
    
    class Meta:
        model = SymptomCheck
        fields = [
            'id', 'patient', 'patient_info', 'symptoms_description',
            'urgency_level', 'urgency_display', 'recommendation',
            'recommended_provider_type', 'confidence_score',
            'possible_conditions', 'possible_conditions_list',
            'follow_up_needed', 'appointment_booked', 'session_id',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_possible_conditions_list(self, obj):
        """Parse JSON string to list"""
        if obj.possible_conditions:
            try:
                return json.loads(obj.possible_conditions)
            except json.JSONDecodeError:
                return []
        return []


class SymptomCheckCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating symptom checks"""
    class Meta:
        model = SymptomCheck
        fields = [
            'symptoms_description', 'urgency_level', 'recommendation',
            'recommended_provider_type', 'confidence_score',
            'possible_conditions', 'follow_up_needed', 'session_id'
        ]
    
    def create(self, validated_data):
        """Add patient from request if authenticated, allow anonymous"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['patient'] = request.user
        
        # Add IP address from request
        if request:
            validated_data['ip_address'] = self.get_client_ip(request)
        
        return super().create(validated_data)
    
    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def validate_possible_conditions(self, value):
        """Validate JSON format for possible conditions"""
        if value:
            try:
                json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError(
                    "Possible conditions must be valid JSON format"
                )
        return value


class SymptomCheckListSerializer(serializers.ModelSerializer):
    """Simplified serializer for symptom check lists"""
    urgency_display = serializers.CharField(source='get_urgency_level_display', read_only=True)
    patient_name = serializers.SerializerMethodField()
    
    class Meta:
        model = SymptomCheck
        fields = [
            'id', 'patient_name', 'symptoms_description', 'urgency_level',
            'urgency_display', 'appointment_booked', 'created_at'
        ]
        read_only_fields = ['id']
    
    def get_patient_name(self, obj):
        if obj.patient:
            return obj.patient.get_full_name()
        return 'Anonymous'


class HealthTipSerializer(serializers.ModelSerializer):
    """Serializer for HealthTip model"""
    category_info = SymptomCategorySerializer(source='category', read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=SymptomCategory.objects.all(),
        source='category',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = HealthTip
        fields = [
            'id', 'title', 'content', 'category', 'category_id',
            'category_info', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class HealthTipListSerializer(serializers.ModelSerializer):
    """Simplified serializer for health tip lists"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = HealthTip
        fields = ['id', 'title', 'category_name', 'created_at']
        read_only_fields = ['id']