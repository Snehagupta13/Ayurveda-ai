"""
Patient State Definition for Ayurveda AI Workflow
Defines the shared state across all agents in the LangGraph workflow
"""

from typing import TypedDict, Optional


class PatientState(TypedDict):
    """
    Shared state object that flows through all agents
    
    Attributes:
        raw_input: Original patient input (symptoms, characteristics)
        structured_symptoms: Parsed and structured symptoms from Symptom Agent
        dosha_analysis: Dosha assessment results from Dosha Agent
        ayurveda_guidance: Personalized recommendations from Guidance Agent
        safety_flags: Safety assessment and contraindications from Safety Agent
        final_response: Final formatted response for patient
    """
    raw_input: str
    structured_symptoms: dict
    dosha_analysis: dict
    ayurveda_guidance: dict
    safety_flags: dict
    final_response: str


class StructuredSymptoms(TypedDict):
    """Format for structured symptoms output"""
    symptoms: list
    properties: list
    severity: str
    duration: str
    additional_notes: str


class DoshaAnalysis(TypedDict):
    """Format for dosha analysis output"""
    primary_dosha: str
    secondary_dosha: Optional[str]
    vata_score: float
    pitta_score: float
    kapha_score: float
    confidence: str
    reasoning: str


class AyurvdaGuidance(TypedDict):
    """Format for Ayurveda guidance output"""
    lifestyle_recommendations: list
    dietary_recommendations: list
    herb_recommendations: list
    exercise_recommendations: list
    when_to_consult: list


class SafetyFlags(TypedDict):
    """Format for safety assessment output"""
    risk_level: str
    safe_to_recommend: bool
    contraindications: list
    warnings: list
    mandatory_consultation: str
    when_to_stop: list
