"""
LangGraph Workflow for Ayurveda AI
Defines the multi-agent orchestration flow with nodes and edges
"""

from typing import Any, Dict
from langgraph.graph import StateGraph, START, END
from state import PatientState


class AyurvedaAIGraph:
    """LangGraph workflow orchestration for Ayurveda AI system"""
    
    def __init__(self, symptom_agent, dosha_agent, guidance_agent, safety_agent, llm):
        """
        Initialize the graph with all agents and LLM
        
        Args:
            symptom_agent: Symptom analysis agent
            dosha_agent: Dosha assessment agent
            guidance_agent: Guidance generation agent
            safety_agent: Safety verification agent
            llm: Language model instance for agent execution
        """
        self.symptom_agent = symptom_agent
        self.dosha_agent = dosha_agent
        self.guidance_agent = guidance_agent
        self.safety_agent = safety_agent
        self.llm = llm
        self.graph = None
        self.app = None
    
    def build_graph(self) -> "AyurvedaAIGraph":
        """
        Build the LangGraph workflow with nodes and edges
        
        Graph Structure:
        START
          ↓
        symptom_node
          ↓
        dosha_node
          ↓
        guidance_node
          ↓
        safety_node
          ↓
        formatter_node
          ↓
        END
        
        Returns:
            Self for method chaining
        """
        # Create state graph
        self.graph = StateGraph(PatientState)
        
        # Add nodes
        self.graph.add_node("symptom_node", self.symptom_analysis_node)
        self.graph.add_node("dosha_node", self.dosha_analysis_node)
        self.graph.add_node("guidance_node", self.guidance_generation_node)
        self.graph.add_node("safety_node", self.safety_verification_node)
        self.graph.add_node("formatter_node", self.format_response_node)
        
        # Add edges - define the workflow connections
        self.graph.add_edge(START, "symptom_node")
        self.graph.add_edge("symptom_node", "dosha_node")
        self.graph.add_edge("dosha_node", "guidance_node")
        self.graph.add_edge("guidance_node", "safety_node")
        self.graph.add_edge("safety_node", "formatter_node")
        self.graph.add_edge("formatter_node", END)
        
        # Compile the graph
        self.app = self.graph.compile()
        
        return self
    
    def symptom_analysis_node(self, state: PatientState) -> Dict[str, Any]:
        """
        Node 1: Analyze and structure patient symptoms
        
        Input: raw_input (patient's description)
        Output: structured_symptoms
        
        Args:
            state: Current patient state
            
        Returns:
            Updated state with structured symptoms
        """
        print(f"🔍 Node: Symptom Analysis")
        
        try:
            # Call symptom agent
            result = self.symptom_agent.analyze(state["raw_input"])
            
            return {
                "structured_symptoms": result,
                "raw_input": state["raw_input"]
            }
        except Exception as e:
            print(f"❌ Error in symptom analysis: {e}")
            return {
                "structured_symptoms": {
                    "symptoms": [],
                    "properties": [],
                    "severity": "unknown",
                    "error": str(e)
                },
                "raw_input": state["raw_input"]
            }
    
    def dosha_analysis_node(self, state: PatientState) -> Dict[str, Any]:
        """
        Node 2: Assess dosha constitution based on structured symptoms
        
        Input: structured_symptoms
        Output: dosha_analysis
        
        Args:
            state: Current patient state with structured symptoms
            
        Returns:
            Updated state with dosha analysis
        """
        print(f"🌿 Node: Dosha Analysis")
        
        try:
            # Extract symptoms for dosha assessment
            symptoms = state["structured_symptoms"].get("symptoms", [])
            properties = state["structured_symptoms"].get("properties", [])
            
            # Call dosha agent
            result = self.dosha_agent.assess({
                "symptoms": symptoms,
                "properties": properties
            })
            
            return {
                "dosha_analysis": result
            }
        except Exception as e:
            print(f"❌ Error in dosha analysis: {e}")
            return {
                "dosha_analysis": {
                    "primary_dosha": "unknown",
                    "confidence": "low",
                    "error": str(e)
                }
            }
    
    def guidance_generation_node(self, state: PatientState) -> Dict[str, Any]:
        """
        Node 3: Generate personalized Ayurvedic guidance
        
        Input: dosha_analysis
        Output: ayurveda_guidance
        
        Args:
            state: Current patient state with dosha analysis
            
        Returns:
            Updated state with guidance recommendations
        """
        print(f"💊 Node: Guidance Generation")
        
        try:
            # Extract dosha and symptoms for guidance
            primary_dosha = state["dosha_analysis"].get("primary_dosha", "unknown")
            symptoms = state["structured_symptoms"].get("symptoms", [])
            
            # Call guidance agent
            result = self.guidance_agent.generate_guidance(
                dosha=primary_dosha,
                condition=", ".join(symptoms) if symptoms else "general wellness"
            )
            
            return {
                "ayurveda_guidance": result
            }
        except Exception as e:
            print(f"❌ Error in guidance generation: {e}")
            return {
                "ayurveda_guidance": {
                    "lifestyle_recommendations": [],
                    "dietary_recommendations": [],
                    "error": str(e)
                }
            }
    
    def safety_verification_node(self, state: PatientState) -> Dict[str, Any]:
        """
        Node 4: Verify safety of all recommendations
        
        CRITICAL: This node ensures all recommendations are safe
        
        Input: ayurveda_guidance, raw_input (contains user context)
        Output: safety_flags, modified ayurveda_guidance if needed
        
        Args:
            state: Current patient state with all previous analysis
            
        Returns:
            Updated state with safety assessment
        """
        print(f"⚠️  Node: Safety Verification")
        
        try:
            # Extract recommendations and context
            guidance = state["ayurveda_guidance"]
            user_input = state["raw_input"]
            
            # Compile recommendation string for safety check
            recommendations = []
            for key, items in guidance.items():
                if isinstance(items, list):
                    recommendations.extend(items)
            
            recommendation_text = " | ".join(recommendations) if recommendations else "General wellness"
            
            # Call safety agent
            result = self.safety_agent.verify_recommendation(
                recommendation=recommendation_text,
                user_context={"raw_input": user_input}
            )
            
            return {
                "safety_flags": result
            }
        except Exception as e:
            print(f"❌ Error in safety verification: {e}")
            return {
                "safety_flags": {
                    "risk_level": "unknown",
                    "safe_to_recommend": False,
                    "mandatory_consultation": "Doctor consultation required due to analysis error",
                    "error": str(e)
                }
            }
    
    def format_response_node(self, state: PatientState) -> Dict[str, Any]:
        """
        Node 5: Format final response for patient display
        
        Combines all analysis into a patient-friendly response
        
        Input: All previous analysis (structured_symptoms, dosha_analysis, 
               ayurveda_guidance, safety_flags)
        Output: final_response (formatted text for display)
        
        Args:
            state: Complete patient state with all analysis
            
        Returns:
            Updated state with formatted final response
        """
        print(f"📋 Node: Response Formatting")
        
        try:
            response_parts = []
            
            # Header
            response_parts.append("=" * 60)
            response_parts.append("🌿 AYURVEDA AI HEALTH GUIDANCE")
            response_parts.append("=" * 60)
            response_parts.append("")
            
            # Symptom Summary
            symptoms = state["structured_symptoms"].get("symptoms", [])
            if symptoms:
                response_parts.append("📋 SYMPTOMS IDENTIFIED:")
                for symptom in symptoms:
                    response_parts.append(f"  • {symptom}")
                response_parts.append("")
            
            # Dosha Analysis
            dosha = state["dosha_analysis"].get("primary_dosha", "Unknown")
            confidence = state["dosha_analysis"].get("confidence", "low")
            reasoning = state["dosha_analysis"].get("reasoning", "")
            
            response_parts.append(f"🌿 DOSHA ANALYSIS:")
            response_parts.append(f"  Primary Dosha: {dosha}")
            response_parts.append(f"  Confidence: {confidence}")
            if reasoning:
                response_parts.append(f"  Reasoning: {reasoning}")
            response_parts.append("")
            
            # Safety Assessment
            risk_level = state["safety_flags"].get("risk_level", "unknown")
            safe = state["safety_flags"].get("safe_to_recommend", False)
            
            response_parts.append(f"⚠️  SAFETY ASSESSMENT:")
            response_parts.append(f"  Risk Level: {risk_level}")
            response_parts.append(f"  Safe to Proceed: {'Yes' if safe else 'No - Consult Doctor'}")
            
            warnings = state["safety_flags"].get("warnings", [])
            if warnings:
                response_parts.append(f"  Warnings:")
                for warning in warnings:
                    response_parts.append(f"    ⚠️  {warning}")
            response_parts.append("")
            
            # Recommendations (if safe)
            if safe:
                guidance = state["ayurveda_guidance"]
                
                lifestyle = guidance.get("lifestyle_recommendations", [])
                if lifestyle:
                    response_parts.append("✅ LIFESTYLE RECOMMENDATIONS:")
                    for item in lifestyle:
                        response_parts.append(f"  • {item}")
                    response_parts.append("")
                
                diet = guidance.get("dietary_recommendations", [])
                if diet:
                    response_parts.append("🍽️  DIETARY RECOMMENDATIONS:")
                    for item in diet:
                        response_parts.append(f"  • {item}")
                    response_parts.append("")
                
                herbs = guidance.get("herb_recommendations", [])
                if herbs:
                    response_parts.append("🌱 HERBAL SUPPORT (for learning):")
                    for item in herbs:
                        response_parts.append(f"  • {item}")
                    response_parts.append("")
                
                exercise = guidance.get("exercise_recommendations", [])
                if exercise:
                    response_parts.append("🏃 EXERCISE RECOMMENDATIONS:")
                    for item in exercise:
                        response_parts.append(f"  • {item}")
                    response_parts.append("")
            else:
                response_parts.append("❌ RECOMMENDATIONS WITHHELD DUE TO SAFETY CONCERNS")
                response_parts.append("")
            
            # When to Consult
            consult = state["safety_flags"].get("mandatory_consultation", "")
            if consult:
                response_parts.append(f"👨‍⚕️  WHEN TO CONSULT:")
                response_parts.append(f"  {consult}")
                response_parts.append("")
            
            # Standard Disclaimer
            response_parts.append("=" * 60)
            response_parts.append("⚠️  IMPORTANT MEDICAL DISCLAIMER")
            response_parts.append("=" * 60)
            response_parts.append("""
This Ayurveda AI system provides EDUCATIONAL WELLNESS INFORMATION only.

It is NOT a medical device and does NOT:
✗ Diagnose diseases
✗ Prescribe treatments  
✗ Replace professional medical advice
✗ Guarantee health outcomes

You MUST:
✓ Always consult qualified healthcare providers
✓ Inform your doctor of any new recommendations
✓ Seek immediate care for emergencies
✓ Not delay professional treatment

By using this system, you acknowledge these limitations.
""")
            response_parts.append("=" * 60)
            
            final_response = "\n".join(response_parts)
            
            return {
                "final_response": final_response
            }
        except Exception as e:
            print(f"❌ Error in response formatting: {e}")
            return {
                "final_response": f"""
ERROR IN PROCESSING

An error occurred while processing your request: {e}

Please consult a healthcare professional directly.

⚠️  IMPORTANT: This system is for educational purposes only.
Always consult qualified healthcare providers before making health decisions.
"""
            }
    
    async def execute_async(self, user_input: str) -> Dict[str, Any]:
        """
        Execute the workflow asynchronously
        
        Args:
            user_input: Patient's raw input (symptoms, characteristics)
            
        Returns:
            Complete state with all analysis and final response
        """
        if self.app is None:
            raise RuntimeError("Graph not built. Call build_graph() first.")
        
        initial_state: PatientState = {
            "raw_input": user_input,
            "structured_symptoms": {},
            "dosha_analysis": {},
            "ayurveda_guidance": {},
            "safety_flags": {},
            "final_response": ""
        }
        
        # Execute the graph
        result = await self.app.ainvoke(initial_state)
        return result
    
    def execute(self, user_input: str) -> Dict[str, Any]:
        """
        Execute the workflow synchronously
        
        Args:
            user_input: Patient's raw input (symptoms, characteristics)
            
        Returns:
            Complete state with all analysis and final response
        """
        if self.app is None:
            raise RuntimeError("Graph not built. Call build_graph() first.")
        
        initial_state: PatientState = {
            "raw_input": user_input,
            "structured_symptoms": {},
            "dosha_analysis": {},
            "ayurveda_guidance": {},
            "safety_flags": {},
            "final_response": ""
        }
        
        print("\n🚀 Starting Ayurveda AI Analysis Pipeline")
        print("=" * 60)
        
        # Execute the graph
        result = self.app.invoke(initial_state)
        
        print("=" * 60)
        print("✅ Analysis Complete\n")
        
        return result
    
    def get_graph_schema(self) -> str:
        """Get the graph schema as string for debugging"""
        if self.graph is None:
            return "Graph not built"
        return str(self.graph.nodes) + "\n" + str(self.graph.edges)
