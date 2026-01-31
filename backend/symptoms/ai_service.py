"""
AI Service for Symptom Analysis
This service integrates with OpenAI or custom AI models to analyze patient symptoms
"""
import json
import os
from typing import Dict, List, Optional
from openai import OpenAI


class SymptomAnalyzerAI:
    """
    AI-powered symptom analyzer using OpenAI GPT models
    Can be replaced with custom ML models
    """
    
    def __init__(self):
        """Initialize OpenAI client"""
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4-turbo-preview"  # or "gpt-3.5-turbo" for faster/cheaper
    
    def analyze_symptoms(self, symptoms_description: str) -> Dict:
        """
        Analyze patient symptoms and return AI recommendations
        
        Args:
            symptoms_description: Patient's description of symptoms
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Create prompt for AI analysis
            prompt = self._create_analysis_prompt(symptoms_description)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent medical advice
                response_format={"type": "json_object"}
            )
            
            # Parse AI response
            ai_response = json.loads(response.choices[0].message.content)
            
            # Format and validate response
            return self._format_analysis_result(ai_response, symptoms_description)
            
        except Exception as e:
            print(f"AI Analysis Error: {str(e)}")
            # Fallback to rule-based analysis
            return self._fallback_analysis(symptoms_description)
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for AI model"""
        return """You are a medical triage AI assistant. Your role is to:
1. Analyze patient symptoms
2. Determine urgency level (emergency, doctor_visit, or home_care)
3. Provide clear recommendations
4. Suggest appropriate healthcare provider type
5. List possible conditions

CRITICAL RULES:
- Always err on the side of caution
- Flag emergency symptoms immediately
- Never provide definitive diagnoses
- Always recommend professional medical evaluation when uncertain
- Use clear, non-technical language

Response must be in JSON format with these fields:
{
    "urgency_level": "emergency|doctor_visit|home_care",
    "recommendation": "detailed recommendation text",
    "recommended_provider_type": "Emergency Room|Primary Care|Specialist Type|Self-care",
    "confidence_score": 0.0-1.0,
    "possible_conditions": ["condition1", "condition2"],
    "red_flags": ["flag1", "flag2"],
    "self_care_tips": ["tip1", "tip2"]
}

EMERGENCY indicators (urgency_level: "emergency"):
- Chest pain, pressure, or tightness
- Difficulty breathing or shortness of breath
- Severe bleeding
- Loss of consciousness or altered mental status
- Severe head injury
- Stroke symptoms (FAST: Face drooping, Arm weakness, Speech difficulty, Time to call 911)
- Severe allergic reaction
- Suicidal thoughts or intent to harm others
- Severe abdominal pain
- High fever with stiff neck or rash

DOCTOR VISIT indicators (urgency_level: "doctor_visit"):
- Persistent fever
- Moderate pain
- Symptoms lasting more than a few days
- Worsening symptoms
- New or unusual symptoms
- Chronic condition management

HOME CARE indicators (urgency_level: "home_care"):
- Mild cold symptoms
- Minor aches and pains
- Slight headache
- Mild fatigue
- Minor skin irritations"""
    
    def _create_analysis_prompt(self, symptoms: str) -> str:
        """Create analysis prompt from symptoms"""
        return f"""Analyze these patient symptoms and provide medical triage:

PATIENT SYMPTOMS:
{symptoms}

Provide your analysis in JSON format following the specified structure."""
    
    def _format_analysis_result(self, ai_response: Dict, original_symptoms: str) -> Dict:
        """Format AI response into database-compatible format"""
        return {
            'symptoms_description': original_symptoms,
            'urgency_level': ai_response.get('urgency_level', 'doctor_visit'),
            'recommendation': ai_response.get('recommendation', 'Please consult a healthcare provider.'),
            'recommended_provider_type': ai_response.get('recommended_provider_type', 'Primary Care Physician'),
            'confidence_score': float(ai_response.get('confidence_score', 0.75)),
            'possible_conditions': json.dumps(ai_response.get('possible_conditions', [])),
            'follow_up_needed': ai_response.get('urgency_level') != 'home_care',
            'ai_metadata': json.dumps({
                'red_flags': ai_response.get('red_flags', []),
                'self_care_tips': ai_response.get('self_care_tips', []),
                'model_used': self.model
            })
        }
    
    def _fallback_analysis(self, symptoms: str) -> Dict:
        """
        Fallback rule-based analysis when AI is unavailable
        This is the basic keyword-based system
        """
        symptoms_lower = symptoms.lower()
        
        # Emergency keywords
        emergency_keywords = [
            'chest pain', 'can\'t breathe', 'difficulty breathing', 
            'shortness of breath', 'severe bleeding', 'unconscious',
            'stroke', 'heart attack', 'severe pain', 'suicide',
            'overdose', 'seizure', 'severe burn'
        ]
        
        # Doctor visit keywords
        doctor_keywords = [
            'fever', 'infection', 'pain', 'injury', 'sick',
            'vomiting', 'diarrhea', 'rash', 'swelling', 'cough'
        ]
        
        # Check for emergency
        if any(keyword in symptoms_lower for keyword in emergency_keywords):
            return {
                'symptoms_description': symptoms,
                'urgency_level': 'emergency',
                'recommendation': 'SEEK IMMEDIATE EMERGENCY CARE. Call 911 or go to the nearest emergency room immediately.',
                'recommended_provider_type': 'Emergency Room',
                'confidence_score': 0.90,
                'possible_conditions': json.dumps(['Medical Emergency - Immediate Evaluation Required']),
                'follow_up_needed': True
            }
        
        # Check for doctor visit
        elif any(keyword in symptoms_lower for keyword in doctor_keywords):
            return {
                'symptoms_description': symptoms,
                'urgency_level': 'doctor_visit',
                'recommendation': 'Schedule an appointment with your primary care physician within 24-48 hours. Monitor your symptoms and seek emergency care if they worsen.',
                'recommended_provider_type': 'Primary Care Physician',
                'confidence_score': 0.75,
                'possible_conditions': json.dumps(['Requires Medical Evaluation']),
                'follow_up_needed': True
            }
        
        # Default to home care
        else:
            return {
                'symptoms_description': symptoms,
                'urgency_level': 'home_care',
                'recommendation': 'Rest, stay hydrated, and monitor your symptoms. Over-the-counter medications may help. Seek medical attention if symptoms worsen or persist for more than a few days.',
                'recommended_provider_type': 'Self-care',
                'confidence_score': 0.70,
                'possible_conditions': json.dumps(['Mild Symptoms - Self-care Appropriate']),
                'follow_up_needed': False
            }


class DoctorRecommendationAI:
    """
    AI service to recommend doctors based on symptoms and location
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def get_recommended_specialties(self, symptoms: str, urgency_level: str) -> List[str]:
        """
        Get recommended medical specialties based on symptoms
        
        Args:
            symptoms: Patient symptoms
            urgency_level: Determined urgency level
            
        Returns:
            List of recommended medical specialties
        """
        if urgency_level == 'emergency':
            return ['Emergency Medicine']
        
        # Use AI to determine specialties
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a medical triage expert. Given symptoms, recommend 1-3 medical specialties that should be consulted. Return only a JSON array of specialty names."
                    },
                    {
                        "role": "user",
                        "content": f"What medical specialties should evaluate these symptoms: {symptoms}"
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('specialties', ['Primary Care', 'Family Medicine'])
            
        except Exception as e:
            print(f"Specialty recommendation error: {str(e)}")
            # Fallback to basic specialties
            return self._get_fallback_specialties(symptoms)
    
    def _get_fallback_specialties(self, symptoms: str) -> List[str]:
        """Fallback specialty recommendation based on keywords"""
        symptoms_lower = symptoms.lower()
        
        specialty_keywords = {
            'Dermatology': ['skin', 'rash', 'acne', 'mole', 'eczema'],
            'Cardiology': ['heart', 'chest pain', 'palpitations'],
            'Orthopedics': ['bone', 'joint', 'fracture', 'sprain'],
            'Gastroenterology': ['stomach', 'digestion', 'nausea', 'diarrhea'],
            'Neurology': ['headache', 'migraine', 'dizziness', 'numbness'],
            'ENT': ['ear', 'nose', 'throat', 'sinus'],
            'Ophthalmology': ['eye', 'vision', 'blind'],
            'Mental Health': ['anxiety', 'depression', 'stress', 'mental'],
            'Pediatrics': ['child', 'baby', 'infant'],
        }
        
        recommended = []
        for specialty, keywords in specialty_keywords.items():
            if any(keyword in symptoms_lower for keyword in keywords):
                recommended.append(specialty)
        
        # Default to primary care if no specialty matches
        if not recommended:
            recommended = ['Primary Care', 'Family Medicine']
        
        return recommended[:3]  # Return max 3 specialties


# Singleton instances
symptom_analyzer = SymptomAnalyzerAI()
doctor_recommender = DoctorRecommendationAI()