# 🌿 Ayurveda AI — Offline Clinical Intelligence

> Fine-tuned MedGemma 4B | 5-Agent LangGraph Pipeline | Multimodal Tongue Analysis | 100% Offline

**Submitted to:** MedGemma Impact Challenge (Kaggle, Feb 2026)  
**Branch:** master  
**Author:** P S Priti Sudha

---

## Problem

Over **1.2 billion people** in South Asia rely on Ayurveda as primary healthcare. Rural practitioners have no AI tools, no reliable internet, and no access to specialist consultations. No AI system exists for Ayurvedic clinical decision support.

---

## Solution

Ayurveda AI is a fully offline clinical intelligence system that provides structured Ayurvedic assessments including:

- Dosha analysis (Vata / Pitta / Kapha)
- Herb recommendations
- Formulations and dosages
- Dietary and lifestyle guidance
- Yoga and physical therapy
- Prognosis and prevention

All processing runs **100% locally** with zero internet dependency.

---

## 📊 Key Results

| Metric | Value |
|--------|-------|
| Base Model | google/medgemma-4b-it (4.3B params) |
| Training Method | LoRA (r=16, alpha=32) |
| Trainable Parameters | 11,898,880 (0.28%) |
| Start Loss | 2.89 |
| Final Train Loss | 0.27 |
| Final Eval Loss | 0.36 |
| Overall Herb Accuracy | 95% |
| Specific Herb Accuracy | 75% |
| Training Data | 446 Ayurvedic treatment plans |
| Hardware | NVIDIA H100 80GB |
| Epochs | 3 |

---

## Project Structure

```
Ayurveda-ai/
│
├── agents/
│   ├── __init__.py
│   ├── symptom_agent.py           # Scores Vata/Pitta/Kapha from symptoms
│   ├── dosha_agent.py             # Maps dosha to treatment principles
│   ├── guidance_agent.py          # Calls fine-tuned MedGemma 4B + LoRA
│   ├── safety_agent.py            # Validates output, appends disclaimer
│   └── vision_agent.py            # Tongue analysis via MedGemma vision
│
├── app/
│   └── main.py                    # Streamlit UI (3 tabs)
│
├── assets/
│   ├── training_curves.png        # 3-panel training chart
│   └── loss_curve_simple.png      # Simple loss curve (2.89 → 0.27)
│
├── dataset/
│   ├── ayurveda_finetune.json     # 446 formatted training examples
│   ├── kaggle_ayurveda/
│   │   └── AyurGenixAI_Dataset.csv
│   └── tongue_samples/
│       ├── coated_tongue.jpg
│       ├── geographic_tongue.jpg
│       ├── healthy_tongue.jpg
│       ├── kapha_tongue.jpg
│       ├── pitta_tongue.jpg
│       └── vata_tongue.jpg
│
├── graph/
│   └── pipeline.py                # LangGraph agent orchestration (CRITICAL)
│
├── models/
│   └── medgemma-ayurveda-lora/
│       └── final/
│           ├── adapter_config.json
│           ├── adapter_model.safetensors
│           ├── chat_template.jinja
│           ├── tokenizer_config.json
│           └── tokenizer.json
│
├── scripts/
│   ├── finetune_medgemma.py       # Fine-tuning (custom training loop)
│   ├── evaluate.py                # Herb recommendation accuracy
│   ├── generate_charts.py         # Training loss charts
│   └── write_agents.py            # Agent file generator
│
├── inference.py                   # Main entry point
├── ayurveda_ai_kaggle.ipynb       # Kaggle submission notebook
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Agent Pipeline

```
Patient Input
(disease, symptoms, age, gender,
 history, medications, stress, diet)
 + optional tongue image
        │
        ▼
[Agent 1] VisionAgent
Analyzes tongue coating and texture
using MedGemma 4B vision capability
(runs only if tongue image provided)
        │
        ▼
[Agent 2] SymptomAgent
Scores Vata / Pitta / Kapha
from symptom keywords
Merges visual dosha (weighted x2)
        │
        ▼
[Agent 3] DoshaAgent
Maps primary dosha to
treatment principles, herbs, yoga
        │
        ▼
[Agent 4] GuidanceAgent
Fine-tuned MedGemma 4B + LoRA
generates full clinical assessment
        │
        ▼
[Agent 5] SafetyAgent
Removes overconfident claims
Appends medical disclaimer
        │
        ▼
Final Structured Assessment
```

**Text mode:** 4 agents (no image)  
**Multimodal mode:** 5 agents (with tongue image)

---

## Installation

```bash
# Clone repository
git clone https://github.com/Snehagupta13/Ayurveda-ai.git
cd Ayurveda-ai
git checkout master

# Create environment
conda create -n MedGemma python=3.12
conda activate MedGemma

# Install dependencies
pip install -r requirements.txt
```

---

## Run Commands (In Order)

```bash
# Step 1 — Activate environment
conda activate MedGemma
cd ~/Ayurveda-ai

# Step 2 — Fine-tune MedGemma
python scripts/finetune_medgemma.py

# Step 3 — Generate training charts
python scripts/generate_charts.py

# Step 4 — Test inference pipeline
python inference.py

# Step 5 — Run evaluation
python scripts/evaluate.py

# Step 6 — Launch Streamlit UI
streamlit run app/main.py --server.port 8501 --server.address 0.0.0.0
```

Open browser at `http://localhost:8501`

---

## Streamlit UI — 3 Tabs

**Tab 1 — Clinical Assessment**  
Enter patient details → 4-agent pipeline → structured Ayurvedic assessment

**Tab 2 — Tongue Analysis (Darshan)**  
Upload tongue photo → 5-agent multimodal pipeline → visual dosha diagnosis

**Tab 3 — Training Results**  
Loss curves, epoch metrics, model configuration, accuracy numbers

---

## Technical Details

**Why a custom training loop?**  
MedGemma 4B uses the Gemma3 architecture which requires explicit `token_type_ids`
during training. Standard frameworks (HuggingFace Trainer, SFTTrainer) do not
handle this automatically. We wrote a custom PyTorch loop with manual
`token_type_ids` injection as zeros.

**Training configuration:**

| Parameter | Value |
|-----------|-------|
| Epochs | 3 |
| Batch size | 4 |
| Learning rate | 2e-4 |
| Precision | bfloat16 |
| Train split | 401 samples |
| Eval split | 45 samples |

**LoRA configuration:**

| Parameter | Value |
|-----------|-------|
| r | 16 |
| alpha | 32 |
| Target modules | q_proj, k_proj, v_proj, o_proj |
| Dropout | 0.05 |
| Task type | CAUSAL_LM |

---

## Dataset

**AyurGenixAI** — 446 Ayurvedic treatment plans covering diseases, herbs,
formulations, diet, and yoga across 34 clinical dimensions.

Source: [Kaggle — AyurGenixAI Dataset](https://www.kaggle.com/datasets/kagglekirti123/ayurgenixai-ayurvedic-dataset)

---

## Impact

- **1.2 billion** people served by Ayurvedic medicine as primary healthcare
- **Zero internet dependency** — deployable in rural clinics today
- **Privacy-first** — all computation local, no data leaves the device
- **AYUSH Ministry alignment** — supports India's national AI health mandate
- **Edge deployment** — runs on local hardware, no cloud required

---

## Disclaimer

This system provides educational Ayurvedic guidance only. It is NOT a medical
diagnosis or prescription. Always consult a qualified Ayurvedic practitioner
(BAMS) and licensed physician before starting any treatment. In emergencies,
contact medical services immediately.