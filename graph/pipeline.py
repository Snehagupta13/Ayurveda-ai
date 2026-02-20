"""
LangGraph multi-agent pipeline for Ayurveda AI.

Text-only flow:
  SymptomAgent -> DoshaAgent -> GuidanceAgent (MedGemma) -> SafetyAgent

Multimodal flow (with tongue image):
  VisionAgent -> SymptomAgent -> DoshaAgent -> GuidanceAgent -> SafetyAgent
"""
try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False

from agents import SymptomAgent, DoshaAgent, GuidanceAgent, SafetyAgent, VisionAgent

_text_pipeline   = None
_vision_pipeline = None

class SequentialPipeline:
    def __init__(self, agents):
        self.agents = agents
    def invoke(self, state: dict) -> dict:
        for agent in self.agents:
            state = agent.run(state)
        return state

def _build_graph(agent_list, entry):
    if not LANGGRAPH_AVAILABLE:
        return SequentialPipeline(agent_list)
    names = [a.__class__.__name__.lower().replace("agent","") for a in agent_list]
    g = StateGraph(dict)
    for name, agent in zip(names, agent_list):
        g.add_node(name, agent.run)
    g.set_entry_point(names[0])
    for i in range(len(names)-1):
        g.add_edge(names[i], names[i+1])
    g.add_edge(names[-1], END)
    return g.compile()

def get_text_pipeline():
    global _text_pipeline
    if _text_pipeline is None:
        _text_pipeline = _build_graph(
            [SymptomAgent(), DoshaAgent(), GuidanceAgent(), SafetyAgent()],
            entry="symptom"
        )
    return _text_pipeline

def get_vision_pipeline():
    global _vision_pipeline
    if _vision_pipeline is None:
        _vision_pipeline = _build_graph(
            [VisionAgent(), SymptomAgent(), DoshaAgent(), GuidanceAgent(), SafetyAgent()],
            entry="vision"
        )
    return _vision_pipeline

def _format_output(result: dict) -> str:
    dosha_scores = result.get("dosha_scores", {})
    vision_info  = ""
    if result.get("tongue_analysis"):
        vision_info = (
            f"VISUAL DARSHAN ANALYSIS:\n"
            f"  Visual Dosha: {result.get('visual_dosha_indicator', 'N/A')}\n"
            f"  Vision Scores: {result.get('dosha_scores_vision', {})}\n"
            f"---\n"
        )
    agent_info = (
        f"AGENT PIPELINE ANALYSIS:\n"
        f"{vision_info}"
        f"  Symptom Dosha Scores : {dosha_scores}\n"
        f"  Primary Imbalance    : {result.get('primary_dosha', 'N/A')}\n"
        f"  Secondary            : {result.get('secondary_dosha', 'N/A')}\n"
        f"  Treatment Principle  : {result.get('dosha_treatment', {}).get('principle', 'N/A')}\n"
        f"  Dosha Herbs          : {result.get('dosha_treatment', {}).get('herbs', 'N/A')}\n"
        f"---\n\n"
    )
    return agent_info + result.get("final_output", "No output generated.")

def run_ayurveda_pipeline(disease, symptoms, age_group="Adult (20-40)",
                           gender="Male", medical_history="None",
                           current_medications="None",
                           stress_levels="Moderate",
                           dietary_habits="Not specified",
                           tongue_image=None) -> str:
    state = {
        "disease":             disease,
        "symptoms":            symptoms,
        "age_group":           age_group,
        "gender":              gender,
        "medical_history":     medical_history,
        "current_medications": current_medications,
        "stress_levels":       stress_levels,
        "dietary_habits":      dietary_habits,
        "tongue_image":        tongue_image,
    }
    pipeline = get_vision_pipeline() if tongue_image else get_text_pipeline()
    result   = pipeline.invoke(state)
    return _format_output(result)
