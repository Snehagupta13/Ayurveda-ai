import streamlit as st
import sys
sys.path.append(".")
from PIL import Image
from inference import get_ayurvedic_assessment
import os

st.set_page_config(
    page_title="Ayurveda AI",
    page_icon="🌿",
    layout="wide"
)

st.title("🌿 Ayurveda AI — Offline Clinical Intelligence")
st.caption(
    "MedGemma 4B (Fine-tuned on AYUSH data) | "
    "5-Agent LangGraph Pipeline | Multimodal Darshan | 100% Offline"
)

# Agent pipeline diagram
with st.expander("How It Works — Agent Pipeline"):
    st.markdown("""
**Text Mode (4 agents):**
```
Patient Input → SymptomAgent → DoshaAgent → GuidanceAgent (MedGemma) → SafetyAgent
```
**Multimodal Mode (5 agents):**
```
Tongue Image → VisionAgent → SymptomAgent → DoshaAgent → GuidanceAgent → SafetyAgent
```
    """)

st.divider()

# ── Tabs: Text | Vision | Charts ─────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📋 Clinical Assessment",
    "👅 Tongue Analysis (Darshan)",
    "📊 Training Results"
])

# ════════════════════════════════════════════════════════════
# TAB 1: Text-based clinical assessment
# ════════════════════════════════════════════════════════════
with tab1:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Patient Information")
        disease   = st.text_input("Disease / Chief Complaint",
                                   placeholder="e.g., Diabetes, Cough, Hypertension",
                                   key="t_disease")
        symptoms  = st.text_area("Symptoms",
                                  placeholder="e.g., frequent urination, fatigue, thirst",
                                  height=100, key="t_symptoms")
        age_group = st.selectbox("Age Group", [
            "Child (0-12)", "Teen (13-19)", "Adult (20-40)",
            "Middle-aged (40-60)", "Senior (60+)", "All ages"
        ], key="t_age")
        gender = st.selectbox("Gender",
                               ["Male", "Female", "Other", "All genders"],
                               key="t_gender")

        st.subheader("Medical Context")
        med_history = st.text_input("Medical History",
                                     placeholder="e.g., Asthma, Heart disease, None",
                                     key="t_history")
        medications = st.text_input("Current Medications",
                                     placeholder="e.g., Metformin, None",
                                     key="t_meds")
        stress      = st.select_slider("Stress Level",
                                        options=["Low","Moderate","High","Very High"],
                                        value="Moderate", key="t_stress")
        diet        = st.text_input("Dietary Habits",
                                     placeholder="e.g., High sugar, Low fiber",
                                     key="t_diet")

        run_btn = st.button("Get Ayurvedic Assessment",
                             type="primary", use_column_width=True, key="t_run")

    with col2:
        st.subheader("Assessment Results")
        if run_btn:
            if not disease or not symptoms:
                st.error("Please fill in Disease and Symptoms.")
            else:
                with st.spinner("Running 4-agent pipeline..."):
                    result = get_ayurvedic_assessment(
                        disease=disease, symptoms=symptoms,
                        age_group=age_group, gender=gender,
                        medical_history=med_history or "None",
                        current_medications=medications or "None",
                        stress_levels=stress,
                        dietary_habits=diet or "Not specified"
                    )
                st.success("Assessment complete!")
                if "---\n\n" in result:
                    meta, output = result.split("---\n\n", 1)
                    with st.expander("Agent Analysis (Dosha Scoring)", expanded=True):
                        st.code(meta)
                    st.markdown(output)
                else:
                    st.markdown(result)
                st.warning("Educational guidance only. Not a medical diagnosis.")
        else:
            st.info("Fill in patient details and click the button.")
            for d, s in [
                ("Diabetes",     "Frequent urination, fatigue, thirst"),
                ("Cough",        "Sore throat, chest congestion"),
                ("Hypertension", "High blood pressure, headache"),
                ("Arthritis",    "Joint pain, morning stiffness"),
            ]:
                with st.expander(d):
                    st.write(f"Symptoms: {s}")

# ════════════════════════════════════════════════════════════
# TAB 2: Tongue analysis (Darshan / Multimodal)
# ════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Ayurvedic Darshan — Tongue Analysis")
    st.info(
        "In Ayurveda, the tongue is a map of the body. "
        "Upload a clear tongue photo for dosha-based visual diagnosis."
    )

    vcol1, vcol2 = st.columns([1, 1])

    with vcol1:
        st.markdown("**Tongue Image**")
        uploaded = st.file_uploader(
            "Upload tongue photo (JPG/PNG)",
            type=["jpg","jpeg","png"],
            key="tongue_upload"
        )

        # Sample images
        st.markdown("**Or use a sample:**")
        sample_dir = "dataset/tongue_samples"
        samples = {}
        if os.path.exists(sample_dir):
            for f in os.listdir(sample_dir):
                if f.endswith((".jpg",".jpeg",".png")):
                    samples[f] = os.path.join(sample_dir, f)

        selected_sample = st.selectbox(
            "Sample tongue images",
            ["None"] + list(samples.keys()),
            key="sample_select"
        )

        # Additional patient info for vision mode
        st.markdown("**Patient Context (optional)**")
        v_disease  = st.text_input("Chief Complaint",
                                    placeholder="e.g., Fatigue, Digestive issues",
                                    key="v_disease")
        v_symptoms = st.text_input("Additional Symptoms",
                                    placeholder="e.g., bloating, low energy",
                                    key="v_symptoms")

        vision_btn = st.button("Analyze Tongue",
                                type="primary", use_column_width=True,
                                key="v_run")

    with vcol2:
        st.subheader("Darshan Analysis Results")

        # Determine image source
        image = None
        if uploaded:
            image = Image.open(uploaded).convert("RGB")
            st.image(image, caption="Uploaded tongue image", width=300)
        elif selected_sample != "None" and selected_sample in samples:
            image = Image.open(samples[selected_sample]).convert("RGB")
            st.image(image, caption=f"Sample: {selected_sample}", width=300)

        if vision_btn:
            if image is None:
                st.error("Please upload a tongue image or select a sample.")
            else:
                with st.spinner("Running 5-agent multimodal pipeline (VisionAgent → MedGemma)..."):
                    result = get_ayurvedic_assessment(
                        disease=v_disease or "Tongue Analysis",
                        symptoms=v_symptoms or "Visual examination requested",
                        tongue_image=image
                    )
                st.success("Darshan analysis complete!")
                if "---\n\n" in result:
                    meta, output = result.split("---\n\n", 1)
                    with st.expander("Agent Analysis + Visual Dosha Scores", expanded=True):
                        st.code(meta)
                    st.markdown(output)
                else:
                    st.markdown(result)
                st.warning("Educational guidance only. Not a medical diagnosis.")

    # Tongue analysis guide
    st.divider()
    st.subheader("Tongue Reading Guide")
    gcol1, gcol2, gcol3 = st.columns(3)
    with gcol1:
        st.markdown("**Vata Tongue**")
        st.markdown("- Dry, rough surface\n- Cracked or fissured\n- Thin, trembling\n- Dark or brownish coating\n- Dry lips")
    with gcol2:
        st.markdown("**Pitta Tongue**")
        st.markdown("- Red tip or edges\n- Yellow/greenish coating\n- Pointed shape\n- Inflamed, tender\n- Sour/bitter taste")
    with gcol3:
        st.markdown("**Kapha Tongue**")
        st.markdown("- White/thick coating\n- Swollen, puffy\n- Scalloped edges\n- Wet, slimy\n- Sweet/salty taste")

# ════════════════════════════════════════════════════════════
# TAB 3: Training results / charts (Gap 2)
# ════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Model Training Results — MedGemma 4B Fine-Tuning")

    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
    mcol1.metric("Start Loss",    "2.9534", delta=None)
    mcol2.metric("Final Loss",    "0.2705", delta="-2.68", delta_color="inverse")
    mcol3.metric("Eval Loss",     "0.3422", delta=None)
    mcol4.metric("Herb Accuracy", "75%",    delta=None)

    st.divider()

    # Show training curves chart
    chart_path = "assets/training_curves.png"
    if os.path.exists(chart_path):
        st.image(chart_path, caption="Training Loss Curves", use_column_width=True)
    else:
        st.warning("Charts not generated yet. Run: python generate_charts.py")
        if st.button("Generate Charts Now"):
            import subprocess
            subprocess.run(["python", "generate_charts.py"])
            st.rerun()

    st.divider()
    st.subheader("Training Configuration")
    ccol1, ccol2 = st.columns(2)
    with ccol1:
        st.markdown("""
**Model:** google/medgemma-4b-it  
**Method:** LoRA (r=16, alpha=32)  
**Target Modules:** q_proj, k_proj, v_proj, o_proj  
**Trainable Params:** 11,898,880 (0.28%)  
**Total Params:** 4,311,978,352  
        """)
    with ccol2:
        st.markdown("""
**Dataset:** AyurGenixAI (446 records)  
**Train/Eval Split:** 401 / 45  
**Epochs:** 3  
**Batch Size:** 4  
**Learning Rate:** 2e-4  
**Hardware:** NVIDIA H100 80GB  
        """)

    st.divider()
    st.subheader("Epoch-by-Epoch Results")
    import pandas as pd
    results_df = pd.DataFrame([
        {"Epoch": 1, "Train Loss": 0.6211, "Eval Loss": 0.3508, "Status": "Learning"},
        {"Epoch": 2, "Train Loss": 0.3087, "Eval Loss": 0.3568, "Status": "Converging"},
        {"Epoch": 3, "Train Loss": 0.2705, "Eval Loss": 0.3422, "Status": "Converged"},
    ])
    st.dataframe(results_df, use_column_width=True, hide_index=True)

st.divider()
st.caption("Privacy: All processing is 100% local. No patient data leaves this device.")
