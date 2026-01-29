"""
Example usage of Ayurveda AI LangGraph workflow
Demonstrates how to initialize and run the complete pipeline
"""

from graph.langgraph_flow import AyurvedaAIGraph
from agents.symptom_agent import SymptomAgent
from agents.dosha_agent import DoshaAgent
from agents.guidance_agent import GuidanceAgent
from agents.safety_agent import SafetyAgent
from models.medgemma_loader import MedGemmaLoader


def main():
    """Main example function showing the complete workflow"""
    
    print("🌿 Initializing Ayurveda AI System...")
    
    # Step 1: Load the language model
    print("\n1️⃣  Loading MedGemma Model...")
    llm_loader = MedGemmaLoader(model_name="medgemma-2b")
    llm = llm_loader.get_model()
    
    # Step 2: Initialize all agents
    print("2️⃣  Initializing Agents...")
    symptom_agent = SymptomAgent(llm)
    dosha_agent = DoshaAgent(llm)
    guidance_agent = GuidanceAgent(llm)
    safety_agent = SafetyAgent(llm)
    
    # Step 3: Build the LangGraph workflow
    print("3️⃣  Building LangGraph Workflow...")
    graph = AyurvedaAIGraph(
        symptom_agent=symptom_agent,
        dosha_agent=dosha_agent,
        guidance_agent=guidance_agent,
        safety_agent=safety_agent,
        llm=llm
    )
    graph.build_graph()
    
    # Step 4: Define patient input
    patient_input = """
    I have joint pain and stiffness, especially in the morning.
    I feel cold easily and prefer warm weather.
    I'm 65 years old and take blood pressure medication.
    My digestion is sometimes irregular.
    """
    
    # Step 5: Execute the workflow
    print("\n4️⃣  Executing Analysis Pipeline...")
    print("=" * 60)
    
    result = graph.execute(patient_input)
    
    # Step 6: Display results
    print("\n5️⃣  FINAL RESPONSE:")
    print(result["final_response"])
    
    # Optional: Print detailed analysis stages
    print("\n\n📊 DETAILED ANALYSIS BREAKDOWN:")
    print("\n1. STRUCTURED SYMPTOMS:")
    print(result["structured_symptoms"])
    
    print("\n2. DOSHA ANALYSIS:")
    print(result["dosha_analysis"])
    
    print("\n3. AYURVEDA GUIDANCE:")
    print(result["ayurveda_guidance"])
    
    print("\n4. SAFETY FLAGS:")
    print(result["safety_flags"])


if __name__ == "__main__":
    main()
