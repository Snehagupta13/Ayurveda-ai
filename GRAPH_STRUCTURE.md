"""
LangGraph Workflow Visualization and Documentation
Complete guide to the Ayurveda AI multi-agent graph
"""

# ============================================================================
# WORKFLOW STRUCTURE
# ============================================================================
"""
Graph Flow Diagram:

START (Entry Point)
  │
  └──> symptom_node
        Input: raw_input (patient description)
        Processing: SymptomAgent.analyze()
        Output: structured_symptoms
        │
        └──> dosha_node
              Input: structured_symptoms
              Processing: DoshaAgent.assess()
              Output: dosha_analysis
              │
              └──> guidance_node
                    Input: dosha_analysis + structured_symptoms
                    Processing: GuidanceAgent.generate_guidance()
                    Output: ayurveda_guidance
                    │
                    └──> safety_node (CRITICAL CHECKPOINT)
                          Input: ayurveda_guidance + raw_input
                          Processing: SafetyAgent.verify_recommendation()
                          Output: safety_flags
                          │
                          └──> formatter_node
                                Input: All previous outputs
                                Processing: Format for patient display
                                Output: final_response
                                │
                                └──> END (Return to User)

Total Nodes: 5
Total Edges: 6 (including START and END)
Sequential Flow: No branching, strictly linear
Safety Checkpoints: 1 (safety_node - gates recommendation delivery)
"""

# ============================================================================
# NODE DEFINITIONS
# ============================================================================

"""
NODE 1: symptom_node
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Purpose: Parse and structure free-text symptoms into standardized form

Input: PatientState["raw_input"]
  Example: "I have joint pain, stiffness in morning, feeling cold"

Agent Method: SymptomAgent.analyze(text: str) → dict

Output: PatientState["structured_symptoms"]
  Structure:
  {
    "symptoms": ["joint pain", "morning stiffness"],
    "properties": ["cold", "stiff"],
    "severity": "moderate",
    "duration": "2 weeks",
    "additional_notes": "..."
  }

Why This Node:
  ✓ Normalizes free-text input
  ✓ Extracts key data points
  ✓ Reduces noise for downstream agents
  ✓ Creates audit trail of patient's actual words
  ✓ Enables deterministic processing


NODE 2: dosha_node
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Purpose: Assess which dosha (constitutional type) is imbalanced

Input: PatientState["structured_symptoms"]
  Uses: symptoms[], properties[]

Agent Method: DoshaAgent.assess(characteristics: dict) → dict

Output: PatientState["dosha_analysis"]
  Structure:
  {
    "primary_dosha": "Vata",
    "secondary_dosha": "Kapha",
    "vata_score": 0.75,
    "pitta_score": 0.45,
    "kapha_score": 0.60,
    "confidence": "high",
    "reasoning": "Cold sensitivity + stiffness align with Vata..."
  }

Why This Node:
  ✓ Provides Ayurvedic context for guidance
  ✓ Personalizes recommendations
  ✓ Explains to patient why certain advice applies
  ✓ Bridges ancient wisdom and modern AI
  ✓ NOT a diagnosis - just pattern identification


NODE 3: guidance_node
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Purpose: Generate personalized wellness recommendations

Input: PatientState["dosha_analysis"] + PatientState["structured_symptoms"]
  Uses: primary_dosha, symptoms

Agent Method: GuidanceAgent.generate_guidance(dosha: str, condition: str) → dict

Output: PatientState["ayurveda_guidance"]
  Structure:
  {
    "lifestyle_recommendations": [
      "Warm oil massage (Abhyanga) 3-4 times weekly",
      "Gentle yoga (Asana) in morning",
      "Warm baths before bed"
    ],
    "dietary_recommendations": [
      "Favor warm foods over cold",
      "Include healthy fats (ghee, sesame oil)",
      "Avoid raw, heavy foods"
    ],
    "herb_recommendations": [
      "Ashwagandha for joint support",
      "Ginger for warming properties"
    ],
    "exercise_recommendations": [
      "Gentle stretching",
      "Walking in warm weather",
      "Avoid strenuous workouts"
    ],
    "when_to_consult": [
      "Pain worsens despite care",
      "New symptoms appear",
      "Difficulty with daily activities"
    ]
  }

Why This Node:
  ✓ Provides actionable recommendations
  ✓ Customized to individual's dosha
  ✓ Holistic (lifestyle + diet + herbs)
  ✓ Includes safety criteria for consultation
  ✓ Educational, not prescriptive


NODE 4: safety_node (🔒 CRITICAL)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Purpose: Verify safety of recommendations and identify contraindications

Input: PatientState["ayurveda_guidance"] + PatientState["raw_input"]
  Uses: All recommendations, user's medical context

Agent Method: SafetyAgent.verify_recommendation(
                  recommendation: str, 
                  user_context: dict
              ) → dict

Output: PatientState["safety_flags"]
  Structure:
  {
    "risk_level": "medium",          # low, medium, high
    "safe_to_recommend": true,       # Boolean gate for formatter
    "contraindications": [],         # Any medical conflicts
    "warnings": [
      "Patient on BP medication",
      "Warm herbs may interact",
      "Monitor symptoms first week"
    ],
    "mandatory_consultation": "Ayurvedic physician + Primary care",
    "when_to_stop": [
      "Allergic reaction",
      "Condition worsens",
      "Prescribed conflicting treatment"
    ]
  }

CRITICAL LOGIC:
  if safety_flags["safe_to_recommend"] == false:
    → formatter_node withholds all recommendations
    → displays warnings instead
    → demands doctor consultation

Why This Node:
  ✓ MAKES THE SYSTEM SAFE FOR PRODUCTION
  ✓ Prevents harm from unsafe combinations
  ✓ Checks medication interactions
  ✓ Flags age-related concerns
  ✓ Gated by boolean flag (can't be bypassed)
  ✓ Creates legal liability protection


NODE 5: formatter_node
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Purpose: Format all outputs into patient-friendly response

Input: ALL previous outputs from state
  Uses: structured_symptoms, dosha_analysis, ayurveda_guidance, safety_flags

Processing Logic:
  1. If safe_to_recommend == false:
     → Display warnings
     → Recommend doctor consultation
     → Skip recommendations entirely
  2. Else:
     → Display symptoms summary
     → Display dosha analysis
     → Display recommendations (lifestyle, diet, herbs, exercise)
     → Add safety notes
  3. Always append:
     → Disclaimer (medical, educational)
     → When to consult
     → Emergency contact guidance

Output: PatientState["final_response"]
  Format: Formatted text string ready for UI display

Example Output Structure:
  ════════════════════════════════════════════════════════════════════════════
  🌿 AYURVEDA AI HEALTH GUIDANCE
  ════════════════════════════════════════════════════════════════════════════

  📋 SYMPTOMS IDENTIFIED:
    • Joint pain
    • Morning stiffness

  🌿 DOSHA ANALYSIS:
    Primary Dosha: Vata
    Confidence: high
    Reasoning: Cold sensitivity + stiffness align with Vata...

  ⚠️  SAFETY ASSESSMENT:
    Risk Level: medium
    Safe to Proceed: Yes - with doctor approval

  ✅ LIFESTYLE RECOMMENDATIONS:
    • Warm oil massage 3-4 times weekly
    • Gentle yoga in morning
    • Warm baths before bed

  🍽️  DIETARY RECOMMENDATIONS:
    • Favor warm foods over cold
    • Include healthy fats
    • Avoid raw foods

  🌱 HERBAL SUPPORT (for learning):
    • Ashwagandha (traditionally used for joint support)
    • Ginger (warming properties)

  👨‍⚕️  WHEN TO CONSULT:
    Consult Ayurvedic physician + Primary care doctor
    
    Stop and see doctor if:
    - Pain worsens despite care
    - New symptoms appear
    - Difficulty with daily activities

  ════════════════════════════════════════════════════════════════════════════
  ⚠️  IMPORTANT MEDICAL DISCLAIMER
  ════════════════════════════════════════════════════════════════════════════
  This system provides EDUCATIONAL information only...
  ════════════════════════════════════════════════════════════════════════════

Why This Node:
  ✓ Transforms technical outputs to patient language
  ✓ Implements safety decisions from safety_node
  ✓ Ensures disclaimers always shown
  ✓ Creates audit trail of what patient receives
  ✓ Handles errors gracefully
"""

# ============================================================================
# STATE FLOW THROUGH NODES
# ============================================================================

"""
Example state progression through all nodes:

INITIAL STATE:
{
  "raw_input": "I have joint pain and stiffness...",
  "structured_symptoms": {},
  "dosha_analysis": {},
  "ayurveda_guidance": {},
  "safety_flags": {},
  "final_response": ""
}
              ↓
        symptom_node
              ↓
AFTER symptom_node:
{
  "raw_input": "I have joint pain and stiffness...",
  "structured_symptoms": {
    "symptoms": ["joint pain", "morning stiffness"],
    "properties": ["cold", "stiff"],
    ...
  },
  "dosha_analysis": {},
  "ayurveda_guidance": {},
  "safety_flags": {},
  "final_response": ""
}
              ↓
        dosha_node
              ↓
AFTER dosha_node:
{
  "raw_input": "I have joint pain and stiffness...",
  "structured_symptoms": { ... },
  "dosha_analysis": {
    "primary_dosha": "Vata",
    "vata_score": 0.75,
    ...
  },
  "ayurveda_guidance": {},
  "safety_flags": {},
  "final_response": ""
}
              ↓
        guidance_node
              ↓
AFTER guidance_node:
{
  "raw_input": "I have joint pain and stiffness...",
  "structured_symptoms": { ... },
  "dosha_analysis": { ... },
  "ayurveda_guidance": {
    "lifestyle_recommendations": [...],
    "dietary_recommendations": [...],
    ...
  },
  "safety_flags": {},
  "final_response": ""
}
              ↓
        safety_node (GATES RECOMMENDATIONS)
              ↓
AFTER safety_node:
{
  "raw_input": "I have joint pain and stiffness...",
  "structured_symptoms": { ... },
  "dosha_analysis": { ... },
  "ayurveda_guidance": { ... },
  "safety_flags": {
    "risk_level": "medium",
    "safe_to_recommend": true,
    ...
  },
  "final_response": ""
}
              ↓
        formatter_node
              ↓
FINAL STATE (ready for display):
{
  "raw_input": "I have joint pain and stiffness...",
  "structured_symptoms": { ... },
  "dosha_analysis": { ... },
  "ayurveda_guidance": { ... },
  "safety_flags": { ... },
  "final_response": "════════════════════════════════════════════════════════════
🌿 AYURVEDA AI HEALTH GUIDANCE
════════════════════════════════════════════════════════════
... [full formatted response] ..."
}
"""

# ============================================================================
# ERROR HANDLING STRATEGY
# ============================================================================

"""
Each node has try-catch error handling:

try:
  Execute agent logic
  Return updated state
except Exception as e:
  Log error
  Return state with error information
  Continue to next node
  Formatter catches error and displays appropriately

This ensures:
  ✓ No node failure blocks entire pipeline
  ✓ Graceful degradation
  ✓ Patient always gets some response
  ✓ Errors are logged for debugging
  ✓ Safety node still verifies before display
"""

# ============================================================================
# USAGE EXAMPLE
# ============================================================================

"""
from graph.langgraph_flow import AyurvedaAIGraph

# Initialize graph
graph = AyurvedaAIGraph(
    symptom_agent=symptom_agent,
    dosha_agent=dosha_agent,
    guidance_agent=guidance_agent,
    safety_agent=safety_agent,
    llm=llm
)

# Build the workflow
graph.build_graph()

# Execute
result = graph.execute("I have joint pain and stiffness...")

# Get final response
print(result["final_response"])

# Access individual analyses
print(result["dosha_analysis"])
print(result["safety_flags"])
"""

# ============================================================================
# INTEGRATION WITH STREAMLIT
# ============================================================================

"""
In app/main.py:

import streamlit as st
from graph.langgraph_flow import AyurvedaAIGraph

# Initialize graph (in sidebar for caching)
@st.cache_resource
def load_graph():
    # Initialize all components
    graph = AyurvedaAIGraph(...).build_graph()
    return graph

graph = load_graph()

# User input
patient_input = st.text_area("Describe your symptoms...")

if st.button("Analyze"):
  result = graph.execute(patient_input)
  st.write(result["final_response"])
  
  with st.expander("View Detailed Analysis"):
    st.json(result["dosha_analysis"])
    st.json(result["safety_flags"])
"""
