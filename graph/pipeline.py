"""
LangGraph multi-agent pipeline for Ayurveda AI.

Flow:
  Patient Input
      │
  SymptomAgent      ← classifies symptoms, scores doshas
      │
  DoshaAgent        ← maps imbalance to treatment principles
      │
  GuidanceAgent     ← calls fine-tuned MedGemma 4B + LoRA
      │
  SafetyAgent       ← validates output, appends disclaimer
      │
  Final Assessment
"""

try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False

from agents import SymptomAgent, DoshaAgent, GuidanceAgent, SafetyAgent


def build_pipeline():
    symptom_agent  = SymptomAgent()
    dosha_agent    = DoshaAgent()
    guidance_agent = GuidanceAgent()
    safety_agent   = SafetyAgent()

    if LANGGRAPH_AVAILABLE:
        # Full LangGraph DAG
        graph = StateGraph(dict)
        graph.add_node("symptom",  symptom_agent.run)
        graph.add_node("dosha",    dosha_agent.run)
        graph.add_node("guidance", guidance_agent.run)
        graph.add_node("safety",   safety_agent.run)

        graph.set_entry_point("symptom")
        graph.add_edge("symptom",  "dosha")
        graph.add_edge("dosha",    "guidance")
        graph.add_edge("guidance", "safety")
        graph.add_edge("safety",   END)

        return graph.compile()
    else:
        # Fallback sequential pipeline (no LangGraph dependency)
        class SequentialPipeline:
            def __init__(self, agents):
                self.agents = agents

            def invoke(self, state: dict) -> dict:
                for agent in self.agents:
                    state = agent.run(state)
                return state

        return SequentialPipeline([
            symptom_agent, dosha_agent, guidance_agent, safety_agent
        ])


# Singleton pipeline instance
_pipeline = None

def get_pipeline():
    global _pipeline
    if _pipeline is None:
        _pipeline = build_pipeline()
    return _pipeline


def run_ayurveda_pipeline(disease, symptoms, age_group="Adult (20-40)",
                           gender="Male", medical_history="None",
                           current_medications="None",
                           stress_levels="Moderate",
                           dietary_habits="Not specified") -> str:
    """Main entry point — runs full 4-agent pipeline."""
    patient_data = {
        "disease":             disease,
        "symptoms":            symptoms,
        "age_group":           age_group,
        "gender":              gender,
        "medical_history":     medical_history,
        "current_medications": current_medications,
        "stress_levels":       stress_levels,
        "dietary_habits":      dietary_habits,
    }

    pipeline = get_pipeline()
    result   = pipeline.invoke(patient_data)

    # Build enriched output with agent metadata prepended
    dosha_info = (
        f"AGENT ANALYSIS:\n"
        f"  Dosha Scores    : {result.get('dosha_scores', {})}\n"
        f"  Primary Imbalance: {result.get('primary_dosha', 'N/A')}\n"
        f"  Secondary        : {result.get('secondary_dosha', 'N/A')}\n"
        f"  Treatment Principle: {result.get('dosha_treatment', {}).get('principle', 'N/A')}\n"
        f"  Suggested Herbs  : {result.get('dosha_treatment', {}).get('herbs', 'N/A')}\n"
        f"---\n\n"
    )

    return dosha_info + result.get("final_output", "No output generated.")
