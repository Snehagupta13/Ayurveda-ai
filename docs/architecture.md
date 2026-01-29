# Ayurveda AI System Architecture

## Vision: Offline Healthcare AI for Real Clinical Environments

This system delivers safe, structured, AI-powered Ayurvedic patient guidance designed for real clinical settings—not perfect lab conditions. It runs entirely offline, uses healthcare-focused open models, and prioritizes patient safety above all.

---

## System Data Flow

```
User Input (Patient)
   ↓
Input Processor (Text / Voice)
   ↓
Orchestrator Agent (LangGraph)
   ↓
┌──────────────────────────────────────┐
│ Multi-Agent System                   │
│                                      │
│ 1. Symptom Understanding Agent       │
│ 2. Dosha Analysis Agent              │
│ 3. Ayurveda Knowledge Agent          │
│ 4. Safety & Contraindication Agent   │
│ 5. Medical Disclaimer Agent          │
│                                      │
└──────────────────────────────────────┘
   ↓
Response Composer (Structured JSON)
   ↓
Offline UI (Web / Mobile / Tablet)
```

---

## System Components

### 1. Frontend (Streamlit UI)
**File:** `app/main.py`

- User-friendly interface for symptom input
- Dosha assessment questionnaire
- Display personalized guidance
- Safety disclaimers and risk warnings

**Runs on:** Localhost, no cloud connection required

### 2. Orchestration Layer
**File:** `graph/langgraph_flow.py`

Uses LangGraph to coordinate multi-agent workflow:

```
User Input
    ↓
Symptom Analysis → Structured Symptoms
    ↓
Dosha Assessment → Dosha Profile
    ↓
Guidance Generation → Recommendations
    ↓
Safety Verification → Risk Assessment
    ↓
Disclaimer Generation → Final Output
```

---

## 🧠 Agent Architecture

### 1. Symptom Understanding Agent
**File:** `agents/symptom_agent.py`

**Role:** Convert free-text symptoms into structured form

**Input:**
```
"I have joint pain, stiffness in morning, feeling cold"
```

**Output:**
```json
{
  "symptoms": ["joint pain", "morning stiffness"],
  "properties": ["cold", "stiff"],
  "duration": "unknown",
  "severity": "moderate"
}
```

**Why This Matters:**
- ✅ Deterministic and auditable
- ✅ Reusable across agents
- ✅ Reduces hallucination risk
- ✅ Easy to validate and debug

---

### 2. Dosha Analysis Agent
**File:** `agents/dosha_agent.py`

**Role:** Analyze possible dosha imbalance (NOT diagnosis)

**Prompt Style:**
```
Based on Ayurvedic principles, infer possible dosha tendencies.
Do not diagnose disease.
Use cautious language.
Flag any uncertainties for medical review.
```

**Output:**
```json
{
  "possible_doshas": ["Vata", "Vata-Pitta"],
  "primary_dosha": "Vata",
  "confidence": "moderate",
  "reasoning": "Joint stiffness and cold sensitivity align with Vata characteristics (cold, dry, irregular)",
  "disclaimer": "This is not a medical diagnosis. Consult an Ayurvedic physician for proper assessment."
}
```

**Key Principles:**
- Identifies patterns, NOT diseases
- Transparent about confidence levels
- Always includes disclaimers
- References Ayurvedic texts, not medical diagnoses

---

### 3. Ayurveda Knowledge Agent
**File:** `agents/guidance_agent.py`

**Role:** Suggest general, non-prescriptive remedies aligned with dosha

**Examples of Safe Output:**
```json
{
  "lifestyle": [
    "Regular warm oil massage (Abhyanga)",
    "Gentle yoga (Asana)",
    "Warm baths"
  ],
  "diet": [
    "Warm foods preferred",
    "Avoid cold, dry foods",
    "Include healthy fats (ghee, sesame oil)"
  ],
  "herbs_for_learning": [
    "Ashwagandha (traditionally used for joint support)",
    "Ginger (warming properties)"
  ],
  "when_to_consult": [
    "Pain worsens despite care",
    "New symptoms appear",
    "Difficulty with daily activities"
  ]
}
```

**Safety Rules:**
- No dosages (unless universally safe)
- Learning-focused language
- Emphasis on timing and consultation
- No replacement for medical advice

---

### 4. Safety & Contraindication Agent
**File:** `agents/safety_agent.py`

**THE MOST CRITICAL AGENT** — This is what makes the system industry-safe.

**Checks Performed:**
- Pregnancy and nursing status
- Chronic conditions (diabetes, hypertension, heart disease)
- Current medications and interactions
- Allergies and sensitivities
- Age-related considerations
- Immunocompromised status

**Decision Logic:**
```
If High Risk:
  → STOP all recommendations
  → Mandate doctor consultation
  → Flag specific contraindications

If Medium Risk:
  → Flag warnings
  → Suggest monitoring
  → Recommend professional review

If Low Risk:
  → Proceed with recommendations
  → Include general precautions
```

**Output:**
```json
{
  "risk_level": "medium",
  "safe_to_recommend": true,
  "warnings": [
    "Patient reports taking blood pressure medication",
    "Some warm herbs may interact; consult pharmacist",
    "Monitor symptoms during first week"
  ],
  "when_to_stop": [
    "If allergic reaction occurs",
    "If condition worsens",
    "If prescribed conflicting treatment"
  ],
  "mandatory_consultation": "Ayurvedic physician + Primary care doctor"
}
```

---

### 5. Medical Disclaimer Agent
**File:** `agents/safety_agent.py`

**Role:** Ensure appropriate disclaimers at every step

**Standard Disclaimer:**
```
This Ayurveda AI system provides educational wellness information based on 
traditional Ayurvedic principles. It is NOT a medical device and does not:

✗ Diagnose diseases
✗ Prescribe treatments
✗ Replace professional medical advice
✗ Guarantee health outcomes

✓ Always consult qualified healthcare providers
✓ Inform your doctor of any new recommendations
✓ Seek immediate care for emergencies
```

---

## Technology Stack

```
┌──────────────────────────┐
│        User (Patient)    │
│  Web UI / Tablet / PC    │
└───────────┬──────────────┘
            │
            ▼
┌──────────────────────────┐
│     Streamlit Frontend   │
│  (Offline, Localhost)    │
└───────────┬──────────────┘
            │
            ▼
┌──────────────────────────┐
│   Orchestration Layer    │
│      (LangGraph)         │
│  Agent State Controller  │
└───────────┬──────────────┘
            │
            ▼
┌─────────────────────────────────────────────┐
│        Multi-Agent Reasoning System          │
│                                             │
│  1. Symptom Structuring Agent                │
│  2. Dosha Inference Agent                    │
│  3. Ayurveda Guidance Agent                  │
│  4. Safety & Contraindication Agent          │
│  5. Disclaimer Generator Agent               │
│                                             │
└───────────┬─────────────────────────────────┘
            │
            ▼
┌──────────────────────────┐
│   MedGemma 2B Model      │
│  Local Inference Engine  │
│ (Ollama / llama.cpp)     │
└──────────────────────────┘
            │
            ▼
┌──────────────────────────┐
│   Response Composer      │
│  (Structured JSON)       │
└──────────────────────────┘
```

### Components

- **Frontend:** Streamlit (offline, localhost)
- **Orchestration:** LangGraph + LangChain
- **Language Model:** MedGemma 2B (healthcare-optimized)
- **Inference:** Ollama or llama.cpp (local execution)
- **Language:** Python 3.12+

---

## Why This Architecture Beats Simple Prompting

| Feature | Simple Chatbot | This System |
|---------|---|---|
| Control | One prompt (unpredictable) | Multi-agent (deterministic) |
| Safety | Hard to enforce | Structured & guarded |
| Auditability | Black box | Every decision traceable |
| Risk Level | High (risky for health) | Low (safety-first design) |
| Maturity | Demo-level | Production-ready |
| Offline Capable | No | Yes, fully offline |

---

## Why Offline Matters

In many clinical settings:

- **Internet is unreliable** — Connectivity can't be guaranteed
- **Patient data must stay private** — HIPAA, local regulations
- **Cloud AI is impractical** — Cost, latency, security concerns
- **Disaster resilience** — Healthcare AI should work anywhere

**Our system works in:**
- Rural clinics
- Mobile health vans
- Community health centers
- Disaster-response settings
- Clinics with limited connectivity

---

## Data Flow in Action

### Example: Patient with Joint Pain

**Input:**
```
Patient: "I have joint pain and stiffness. I'm 65 years old, on blood pressure medication."
```

**Agent 1 - Symptom Understanding:**
```json
{
  "symptoms": ["joint pain", "morning stiffness"],
  "age": 65,
  "medications": ["blood pressure drug"]
}
```

**Agent 2 - Dosha Analysis:**
```json
{
  "possible_dosha": "Vata with Kapha involvement",
  "confidence": "moderate",
  "reasoning": "Age + stiffness suggest Vata-Kapha imbalance"
}
```

**Agent 3 - Guidance:**
```json
{
  "recommendations": [
    "Warm oil massage",
    "Ginger in diet",
    "Gentle movement"
  ]
}
```

**Agent 4 - Safety Check:**
```json
{
  "risk_level": "medium",
  "warning": "Blood pressure medication may interact with warm spice intake",
  "action": "Consult doctor before dietary changes"
}
```

**Agent 5 - Disclaimer:**
```
This is general wellness information, not medical treatment.
Always consult your doctor before making health changes.
```

---

## Future Enhancements

### Phase 1: Core System (Current)
- ✅ Multi-agent architecture
- ✅ Offline operation
- ✅ Safety-first design
- ✅ Structured outputs

### Phase 2: Knowledge Enhancement
- Fine-tuning on AYUSH guidelines
- Integration with verified Ayurveda databases
- Expanded herb-drug interaction database
- Professional provider network

### Phase 3: Integration
- Electronic health records (EHR) integration
- Mobile app for patients
- Multi-language support
- Analytics dashboard for providers

### Phase 4: Expansion
- Expand beyond Ayurveda (TCM, Unani, etc.)
- Post-discharge support
- Chronic disease management
- Integration with telehealth platforms

---

## Safety Principles

1. **Non-Medical Claims** — Guidance only, no diagnosis
2. **Informed Consent** — Clear disclaimers at every step
3. **Evidence-Based** — Uses peer-reviewed Ayurvedic knowledge
4. **Conservative** — When uncertain, recommend professional consultation
5. **Auditable** — Every decision is logged and traceable

---

## Deployment Scenarios

### Clinic Mode (Primary)
```
Doctor's Office / Clinic
    ↓
Single laptop running Ayurveda AI
    ↓
Patient uses local Streamlit UI
    ↓
All data stays in clinic
    ↓
Offline, fully private
```

### Demo Mode (Secondary)
```
Public demo server (optional)
    ↓
Limited to safe, generic inputs
    ↓
No patient data collected
    ↓
Showcases system capabilities
    ↓
Redirects users to local deployment
```

---

## Success Metrics

- **Safety:** Zero critical safety incidents
- **Compliance:** 100% disclaimer coverage
- **Usability:** Patient comprehension >80%
- **Accuracy:** Dosha assessment alignment >75%
- **Adoption:** Used in 10+ clinical settings

