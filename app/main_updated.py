"""
Streamlit UI Integration with LangGraph Workflow
Updated main.py with full workflow integration
"""

import streamlit as st
import json
from graph.langgraph_flow import AyurvedaAIGraph
from agents.symptom_agent import SymptomAgent
from agents.dosha_agent import DoshaAgent
from agents.guidance_agent import GuidanceAgent
from agents.safety_agent import SafetyAgent
from models.medgemma_loader import MedGemmaLoader


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="🌿 Ayurveda AI Health Assistant",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
    }
    .header-text {
        text-align: center;
        font-size: 2.5em;
        color: #1f7f3d;
        margin: 20px 0;
    }
    .disclaimer-box {
        background-color: #fff3cd;
        border: 2px solid #ffc107;
        padding: 20px;
        border-radius: 5px;
        margin: 20px 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 2px solid #28a745;
        padding: 20px;
        border-radius: 5px;
        margin: 20px 0;
    }
    .warning-box {
        background-color: #f8d7da;
        border: 2px solid #f5c6cb;
        padding: 20px;
        border-radius: 5px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# INITIALIZE GRAPH (CACHED)
# ============================================================================

@st.cache_resource
def load_ayurveda_graph():
    """
    Initialize and build the Ayurveda AI graph
    Cached to run only once per session
    """
    with st.spinner("🌿 Initializing Ayurveda AI System..."):
        try:
            # Load model
            llm_loader = MedGemmaLoader(model_name="medgemma-2b", device="cpu")
            llm = llm_loader.get_model()
            
            # Initialize agents
            symptom_agent = SymptomAgent(llm)
            dosha_agent = DoshaAgent(llm)
            guidance_agent = GuidanceAgent(llm)
            safety_agent = SafetyAgent(llm)
            
            # Build graph
            graph = AyurvedaAIGraph(
                symptom_agent=symptom_agent,
                dosha_agent=dosha_agent,
                guidance_agent=guidance_agent,
                safety_agent=safety_agent,
                llm=llm
            )
            graph.build_graph()
            
            return graph
        except Exception as e:
            st.error(f"Error initializing system: {e}")
            return None


# ============================================================================
# MAIN UI
# ============================================================================

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown("""
    <div class="header-text">🌿 Ayurveda AI Health Assistant</div>
    """, unsafe_allow_html=True)
    
    st.subheader("Your Personalized Ayurvedic Wellness Guidance (Educational Only)")
    
    # Important Disclaimer
    st.markdown("""
    <div class="disclaimer-box">
    <h4>⚠️ IMPORTANT MEDICAL DISCLAIMER</h4>
    <p>
    This Ayurveda AI system provides <strong>EDUCATIONAL WELLNESS INFORMATION</strong> only.
    It is NOT a medical device and does NOT diagnose diseases, prescribe treatments, 
    or replace professional medical advice.
    </p>
    <p>
    <strong>Always consult qualified healthcare providers before making health decisions.</strong>
    </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title("📋 Navigation")
        
        # About section
        with st.expander("ℹ️ About This System", expanded=False):
            st.write("""
            This system uses AI-powered agents to provide personalized Ayurvedic guidance based on:
            
            1. **Symptom Analysis** — Understanding your health concerns
            2. **Dosha Assessment** — Identifying your Ayurvedic constitution
            3. **Personalized Guidance** — Tailored recommendations
            4. **Safety Verification** — Ensuring recommendations are safe for you
            
            All analysis happens offline on this computer. Your data never leaves this device.
            """)
        
        # Instructions
        with st.expander("📖 How to Use", expanded=True):
            st.write("""
            1. **Describe Your Symptoms** in the input box below
            2. Click **"Analyze My Health"** button
            3. View **Detailed Analysis** and recommendations
            4. Follow up with healthcare professionals as needed
            
            **What to Include:**
            - Current symptoms or concerns
            - How long they've been happening
            - Relevant lifestyle habits
            - Age and any existing health conditions
            - Any medications you take
            """)
        
        st.divider()
        
        # System Status
        st.subheader("⚙️ System Status")
        graph = load_ayurveda_graph()
        if graph is not None:
            st.success("✅ Ayurveda AI is ready")
        else:
            st.error("❌ System initialization failed")
    
    # Main Content Area
    st.divider()
    
    # Input Section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("🏥 Describe Your Health Concern")
        st.write("Provide as much detail as helpful:")
        
        # Example button to populate sample text
        sample_text = """I have joint pain and stiffness, especially in the morning. I feel cold easily and prefer warm weather. I'm 65 years old and take blood pressure medication. My digestion is sometimes irregular."""
        
        if st.button("📝 Load Example Input", use_container_width=True):
            st.session_state.patient_input = sample_text
    
    # Input textarea
    patient_input = st.text_area(
        "Your Symptoms & Health Info:",
        value=st.session_state.get("patient_input", ""),
        height=150,
        placeholder="Example: I have joint pain and stiffness, especially in the morning...",
        key="patient_input"
    )
    
    # Analysis button
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        analyze_button = st.button(
            "🔍 Analyze My Health",
            use_container_width=True,
            type="primary"
        )
    
    with col2:
        clear_button = st.button("🗑️ Clear", use_container_width=True)
    
    if clear_button:
        st.session_state.patient_input = ""
        st.session_state.analysis_result = None
        st.rerun()
    
    # Analysis execution
    if analyze_button:
        if not patient_input.strip():
            st.error("❌ Please describe your health concern first")
            return
        
        if graph is None:
            st.error("❌ System is not initialized. Please refresh the page.")
            return
        
        # Execute analysis
        with st.spinner("🔄 Analyzing your health concern... This may take a minute."):
            try:
                result = graph.execute(patient_input)
                st.session_state.analysis_result = result
            except Exception as e:
                st.error(f"Error during analysis: {e}")
                return
    
    # Display results
    if "analysis_result" in st.session_state and st.session_state.analysis_result:
        result = st.session_state.analysis_result
        
        st.divider()
        
        # Main response (nicely formatted)
        st.subheader("📋 Your Personalized Guidance")
        st.text(result["final_response"])
        
        st.divider()
        
        # Detailed Analysis Tabs
        st.subheader("🔬 Detailed Analysis Breakdown")
        
        tab1, tab2, tab3, tab4 = st.tabs(
            ["Symptoms", "Dosha Analysis", "Recommendations", "Safety Assessment"]
        )
        
        with tab1:
            st.write("**Structured Symptoms**")
            symptoms = result["structured_symptoms"]
            
            col1, col2 = st.columns(2)
            with col1:
                if symptoms.get("symptoms"):
                    st.write("**Identified Symptoms:**")
                    for symptom in symptoms["symptoms"]:
                        st.write(f"• {symptom}")
            
            with col2:
                if symptoms.get("properties"):
                    st.write("**Properties:**")
                    for prop in symptoms["properties"]:
                        st.write(f"• {prop}")
            
            if symptoms.get("severity"):
                st.write(f"**Severity:** {symptoms['severity']}")
            if symptoms.get("duration"):
                st.write(f"**Duration:** {symptoms['duration']}")
            
            with st.expander("📊 View Raw Data"):
                st.json(symptoms)
        
        with tab2:
            st.write("**Dosha Constitution Analysis**")
            dosha = result["dosha_analysis"]
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Primary Dosha", dosha.get("primary_dosha", "Unknown"))
                st.metric("Confidence", dosha.get("confidence", "Unknown"))
            
            with col2:
                st.metric("Secondary Dosha", dosha.get("secondary_dosha", "None"))
            
            # Dosha scores visualization
            if all(key in dosha for key in ["vata_score", "pitta_score", "kapha_score"]):
                st.write("**Dosha Scores:**")
                dosha_scores = {
                    "Vata": dosha["vata_score"],
                    "Pitta": dosha["pitta_score"],
                    "Kapha": dosha["kapha_score"]
                }
                st.bar_chart(dosha_scores)
            
            if dosha.get("reasoning"):
                st.write(f"**Reasoning:** {dosha['reasoning']}")
            
            with st.expander("📊 View Raw Data"):
                st.json(dosha)
        
        with tab3:
            st.write("**Personalized Recommendations**")
            guidance = result["ayurveda_guidance"]
            
            # Check safety before showing recommendations
            if result["safety_flags"].get("safe_to_recommend"):
                if guidance.get("lifestyle_recommendations"):
                    st.write("**🧘 Lifestyle Recommendations:**")
                    for item in guidance["lifestyle_recommendations"]:
                        st.write(f"• {item}")
                
                if guidance.get("dietary_recommendations"):
                    st.write("**🍽️ Dietary Recommendations:**")
                    for item in guidance["dietary_recommendations"]:
                        st.write(f"• {item}")
                
                if guidance.get("herb_recommendations"):
                    st.write("**🌱 Herbal Support (For Learning):**")
                    for item in guidance["herb_recommendations"]:
                        st.write(f"• {item}")
                
                if guidance.get("exercise_recommendations"):
                    st.write("**🏃 Exercise Recommendations:**")
                    for item in guidance["exercise_recommendations"]:
                        st.write(f"• {item}")
            else:
                st.markdown("""
                <div class="warning-box">
                <h4>⚠️ Recommendations Withheld</h4>
                <p>Based on the safety assessment, recommendations have been withheld pending 
                professional medical consultation. Please see your healthcare provider.</p>
                </div>
                """, unsafe_allow_html=True)
            
            with st.expander("📊 View Raw Data"):
                st.json(guidance)
        
        with tab4:
            st.write("**Safety Assessment**")
            safety = result["safety_flags"]
            
            col1, col2 = st.columns(2)
            with col1:
                risk_level = safety.get("risk_level", "Unknown")
                risk_color = "🟢" if risk_level == "low" else "🟡" if risk_level == "medium" else "🔴"
                st.metric("Risk Level", f"{risk_color} {risk_level}")
            
            with col2:
                safe = safety.get("safe_to_recommend", False)
                st.metric("Safe to Proceed", "✅ Yes" if safe else "❌ No")
            
            if safety.get("warnings"):
                st.write("**⚠️ Warnings:**")
                for warning in safety["warnings"]:
                    st.warning(warning)
            
            if safety.get("contraindications"):
                st.write("**🛑 Contraindications:**")
                for contra in safety["contraindications"]:
                    st.error(contra)
            
            if safety.get("mandatory_consultation"):
                st.markdown(f"""
                <div class="warning-box">
                <h4>👨‍⚕️ Required Consultation</h4>
                <p><strong>{safety['mandatory_consultation']}</strong></p>
                </div>
                """, unsafe_allow_html=True)
            
            if safety.get("when_to_stop"):
                st.write("**When to Stop and Seek Help:**")
                for item in safety["when_to_stop"]:
                    st.write(f"• {item}")
            
            with st.expander("📊 View Raw Data"):
                st.json(safety)
        
        st.divider()
        
        # Download results
        st.subheader("💾 Export Results")
        
        result_json = json.dumps(result, indent=2)
        st.download_button(
            label="📥 Download Analysis (JSON)",
            data=result_json,
            file_name="ayurveda_analysis.json",
            mime="application/json"
        )
        
        # Additional resources
        st.divider()
        st.subheader("📚 Additional Resources")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("""
            **🏥 Next Steps:**
            1. Consult your primary healthcare provider
            2. Share this analysis with your doctor
            3. Consult an Ayurvedic physician
            4. Begin only with professional approval
            """)
        
        with col2:
            st.success("""
            **✅ This System:**
            • Runs completely offline
            • Uses healthcare-optimized AI
            • Prioritizes your safety
            • Respects your privacy
            • Requires professional guidance
            """)


# ============================================================================
# RUN APP
# ============================================================================

if __name__ == "__main__":
    main()
