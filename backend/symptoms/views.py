# ==================== symptoms/views.py ====================
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import SymptomCategory, SymptomCheck, HealthTip
from .serializers import (
    SymptomCategorySerializer, SymptomCheckSerializer,
    SymptomCheckCreateSerializer, SymptomCheckListSerializer,
    HealthTipSerializer, HealthTipListSerializer
)


class SymptomCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for SymptomCategory CRUD operations
    """
    queryset = SymptomCategory.objects.all()
    serializer_class = SymptomCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name']


class SymptomCheckViewSet(viewsets.ModelViewSet):
    """
    ViewSet for SymptomCheck operations
    Allows anonymous users to check symptoms
    """
    queryset = SymptomCheck.objects.select_related('patient')
    serializer_class = SymptomCheckSerializer
    permission_classes = [permissions.AllowAny]  # Allow anonymous checks
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['urgency_level', 'follow_up_needed', 'appointment_booked']
    ordering_fields = ['created_at', 'urgency_level']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Filter queryset based on user authentication
        Authenticated users see only their checks, anonymous users see nothing
        """
        if self.request.user.is_authenticated:
            if self.request.user.is_staff:
                return SymptomCheck.objects.all()
            return SymptomCheck.objects.filter(patient=self.request.user)
        
        # Anonymous users can create but not list
        return SymptomCheck.objects.none()
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'create':
            return SymptomCheckCreateSerializer
        elif self.action == 'list':
            return SymptomCheckListSerializer
        return SymptomCheckSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create symptom check with AI analysis
        This is where you'd integrate your AI model
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Here you would call your AI service to analyze symptoms
        # For now, we'll just save the data as provided
        symptom_check = serializer.save()
        
        # Return full details
        output_serializer = SymptomCheckSerializer(symptom_check)
        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def analyze(self, request):
        """
        Analyze symptoms and provide recommendations
        This is the main AI endpoint
        """
        symptoms = request.data.get('symptoms_description', '')
        
        if not symptoms:
            return Response(
                {'error': 'Symptoms description is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # TODO: Integrate with AI model here
        # For now, return a mock analysis
        
        # Mock AI analysis
        analysis = self._mock_ai_analysis(symptoms)
        
        # Create symptom check record
        serializer = SymptomCheckCreateSerializer(
            data=analysis,
            context={'request': request}
        )
        
        if serializer.is_valid():
            symptom_check = serializer.save()
            output_serializer = SymptomCheckSerializer(symptom_check)
            return Response(output_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _mock_ai_analysis(self, symptoms):
        """
        Mock AI analysis - replace with actual AI service
        """
        symptoms_lower = symptoms.lower()
        
        # Simple keyword-based urgency detection (replace with real AI)
        if any(word in symptoms_lower for word in ['severe', 'chest pain', 'bleeding', 'unconscious']):
            urgency = 'emergency'
            recommendation = 'Seek immediate emergency care. Call 911 or go to the nearest emergency room.'
            provider_type = 'Emergency Room'
        elif any(word in symptoms_lower for word in ['fever', 'pain', 'injury', 'infection']):
            urgency = 'doctor_visit'
            recommendation = 'Schedule an appointment with your doctor within 24-48 hours.'
            provider_type = 'Primary Care Physician'
        else:
            urgency = 'home_care'
            recommendation = 'Monitor symptoms. Rest and stay hydrated. Seek care if symptoms worsen.'
            provider_type = 'Self-care'
        
        return {
            'symptoms_description': symptoms,
            'urgency_level': urgency,
            'recommendation': recommendation,
            'recommended_provider_type': provider_type,
            'confidence_score': 0.85,
            'possible_conditions': '["Common Cold", "Flu", "Viral Infection"]',
            'follow_up_needed': urgency != 'home_care'
        }
    
    @action(detail=True, methods=['post'])
    def book_appointment(self, request, pk=None):
        """Mark that user has booked appointment for this symptom check"""
        symptom_check = self.get_object()
        symptom_check.appointment_booked = True
        symptom_check.save()
        
        serializer = self.get_serializer(symptom_check)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get symptom check statistics (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = SymptomCheck.objects.all()
        
        stats = {
            'total_checks': queryset.count(),
            'emergency': queryset.filter(urgency_level='emergency').count(),
            'doctor_visit': queryset.filter(urgency_level='doctor_visit').count(),
            'home_care': queryset.filter(urgency_level='home_care').count(),
            'appointments_booked': queryset.filter(appointment_booked=True).count(),
            'follow_up_needed': queryset.filter(follow_up_needed=True).count()
        }
        
        return Response(stats)


class HealthTipViewSet(viewsets.ModelViewSet):
    """
    ViewSet for HealthTip CRUD operations
    """
    queryset = HealthTip.objects.select_related('category')
    serializer_class = HealthTipSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Only show active tips to non-staff users"""
        if self.request.user.is_staff:
            return HealthTip.objects.all()
        return HealthTip.objects.filter(is_active=True)
    
    def get_serializer_class(self):
        """Use simplified serializer for list view"""
        if self.action == 'list':
            return HealthTipListSerializer
        return HealthTipSerializer
    
    @action(detail=False, methods=['get'])
    def random(self, request):
        """Get random health tips"""
        count = int(request.query_params.get('count', 5))
        tips = self.get_queryset().order_by('?')[:count]
        serializer = self.get_serializer(tips, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get health tips grouped by category"""
        category_id = request.query_params.get('category_id')
        
        if not category_id:
            return Response(
                {'error': 'category_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tips = self.get_queryset().filter(category_id=category_id)
        serializer = self.get_serializer(tips, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def daily_tip(self, request):
        """Get daily health tip (could be cached)"""
        from datetime import date
        
        # Use date as seed for consistent daily tip
        today = date.today()
        tip_index = today.toordinal() % self.get_queryset().count()
        
        tip = self.get_queryset()[tip_index:tip_index + 1].first()
        
        if tip:
            serializer = self.get_serializer(tip)
            return Response(serializer.data)
        
        return Response(
            {'message': 'No health tips available'},
            status=status.HTTP_404_NOT_FOUND
        )