"""
Example: Multi-modal Input Integration with LangGraph
Demonstrates text and voice input flowing into the Ayurveda AI graph
"""

from input import TextInputHandler, VoiceInputHandler, SpeechToTextProcessor
from graph.langgraph_flow import AyurvedaAIGraph


def example_text_input():
    """
    Example 1: Simple text input
    User types symptoms directly
    """
    print("\n" + "="*80)
    print("EXAMPLE 1: Text Input")
    print("="*80)
    
    handler = TextInputHandler()
    
    try:
        symptoms = handler.get_input("\n📝 Describe your symptoms: ")
        
        # Validate
        if handler.validate_input(symptoms):
            print(f"✅ Input accepted: {symptoms[:50]}...")
            return symptoms
        else:
            print("❌ Input validation failed")
            return None
            
    except KeyboardInterrupt:
        print("\n⚠️  Input cancelled")
        return None


def example_voice_input():
    """
    Example 2: Voice recording + transcription
    User speaks symptoms, Whisper converts to text
    """
    print("\n" + "="*80)
    print("EXAMPLE 2: Voice Input with Transcription")
    print("="*80)
    
    try:
        # Step 1: Record audio
        voice_handler = VoiceInputHandler(sample_rate=16000)
        print("\n🎤 Recording for 10 seconds...")
        audio_file = voice_handler.record_audio(duration=10)
        print(f"✅ Recording saved: {audio_file}")
        
        # Step 2: Convert audio to text
        print("\n🔄 Transcribing audio (using whisper-small)...")
        transcriber = SpeechToTextProcessor(
            model_name="small",  # CPU-optimized
            device="cpu"
        )
        symptoms = transcriber.transcribe(audio_file)
        print(f"✅ Transcription: {symptoms}")
        
        return symptoms
        
    except ImportError as e:
        print(f"⚠️  {e}")
        print("Install with: pip install openai-whisper pyaudio")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def example_integrate_with_graph(raw_input: str):
    """
    Example 3: Send input to LangGraph workflow
    """
    if not raw_input:
        print("❌ No input to process")
        return
    
    print("\n" + "="*80)
    print("EXAMPLE 3: Process with LangGraph")
    print("="*80)
    
    print(f"\n📥 Input: {raw_input}")
    
    try:
        # Initialize graph (agents need implementation)
        print("\n🔄 Building LangGraph workflow...")
        graph = AyurvedaAIGraph().build_graph()
        
        # Execute
        print("⏳ Processing through 5-node workflow...")
        result = graph.execute(raw_input)
        
        # Display results
        print("\n✅ Processing complete!")
        print("\n" + "="*80)
        print("RESULTS")
        print("="*80)
        
        if "structured_symptoms" in result:
            print(f"\n1️⃣  Symptoms Analysis:")
            print(f"   {result['structured_symptoms']}")
        
        if "dosha_analysis" in result:
            print(f"\n2️⃣  Dosha Analysis:")
            print(f"   {result['dosha_analysis']}")
        
        if "ayurveda_guidance" in result:
            print(f"\n3️⃣  Guidance:")
            print(f"   {result['ayurveda_guidance']}")
        
        if "safety_flags" in result:
            print(f"\n4️⃣  Safety Gate:")
            safe = result['safety_flags'].get('safe_to_recommend', False)
            print(f"   Safe to recommend: {'✅ YES' if safe else '❌ NO'}")
        
        if "final_response" in result:
            print(f"\n5️⃣  Final Response:")
            print(f"   {result['final_response']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_complete_workflow(input_method: str = "text"):
    """
    Complete end-to-end example
    """
    print("\n" + "█"*80)
    print("█" + " "*78 + "█")
    print("█  AYURVEDA AI - MULTI-MODAL INPUT EXAMPLE" + " "*35 + "█")
    print("█" + " "*78 + "█")
    print("█"*80)
    
    # Get input (choose method)
    if input_method == "text":
        print("\n🔹 Using TEXT INPUT")
        symptoms = example_text_input()
    
    elif input_method == "voice":
        print("\n🔹 Using VOICE INPUT")
        symptoms = example_voice_input()
    
    else:
        print(f"Unknown input method: {input_method}")
        return
    
    # Process with graph
    if symptoms:
        example_integrate_with_graph(symptoms)
    
    print("\n" + "█"*80)
    print("✨ Example complete!")
    print("█"*80)


# ============================================================================
# STREAMLIT INTEGRATION EXAMPLE
# ============================================================================

def streamlit_complete_interface():
    """
    Example: Complete Streamlit UI with multi-modal input
    """
    import streamlit as st
    
    st.set_page_config(page_title="Ayurveda AI", layout="wide")
    st.title("🌿 Ayurveda AI Health Advisor")
    
    # Input method selection
    input_mode = st.radio(
        "How would you like to provide symptoms?",
        ["📝 Type", "🎤 Voice Record"]
    )
    
    symptoms = None
    
    if input_mode == "📝 Type":
        symptoms = st.text_area(
            "Describe your symptoms:",
            placeholder="Example: I have joint pain, feel cold, poor digestion...",
            height=120
        )
    
    else:  # Voice
        st.info("🎤 Click the button below to record your symptoms")
        
        voice_handler = VoiceInputHandler()
        audio_file = voice_handler.record_async()
        
        if audio_file:
            st.success(f"✅ Audio recorded: {audio_file}")
            
            if st.button("🔄 Transcribe Audio"):
                try:
                    processor = SpeechToTextProcessor(model_name="small")
                    symptoms = processor.transcribe(audio_file)
                    st.text_area("Transcribed Text:", value=symptoms, disabled=True)
                except Exception as e:
                    st.error(f"Transcription error: {e}")
    
    # Process with graph
    if symptoms and st.button("🔍 Analyze"):
        try:
            graph = AyurvedaAIGraph().build_graph()
            result = graph.execute(symptoms)
            
            # Display results in tabs
            tab1, tab2, tab3, tab4 = st.tabs(
                ["Symptoms", "Dosha", "Guidance", "Safety"]
            )
            
            with tab1:
                st.json(result.get("structured_symptoms", {}))
            
            with tab2:
                st.json(result.get("dosha_analysis", {}))
            
            with tab3:
                st.write(result.get("ayurveda_guidance", ""))
            
            with tab4:
                safety = result.get("safety_flags", {})
                if safety.get("safe_to_recommend"):
                    st.success("✅ Safe to proceed with recommendations")
                else:
                    st.warning("⚠️  Medical consultation recommended")
        
        except Exception as e:
            st.error(f"Error: {e}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        method = sys.argv[1].lower()
    else:
        method = "text"
    
    print(f"\nRunning example with input method: {method}")
    example_complete_workflow(input_method=method)
