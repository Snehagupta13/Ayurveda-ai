"""
inference.py — Public API for Ayurveda AI.
Routes through 4-agent (text) or 5-agent (text + vision) pipeline.
"""
from graph.pipeline import run_ayurveda_pipeline

def get_ayurvedic_assessment(disease, symptoms,
                              age_group="Adult (20-40)",
                              gender="Male",
                              medical_history="None",
                              current_medications="None",
                              stress_levels="Moderate",
                              dietary_habits="Not specified",
                              tongue_image=None) -> str:
    """
    Main entry point.
    tongue_image: PIL.Image or None
    If tongue_image provided → 5-agent multimodal pipeline
    If None                 → 4-agent text pipeline
    """
    return run_ayurveda_pipeline(
        disease=disease, symptoms=symptoms,
        age_group=age_group, gender=gender,
        medical_history=medical_history,
        current_medications=current_medications,
        stress_levels=stress_levels,
        dietary_habits=dietary_habits,
        tongue_image=tongue_image
    )

if __name__ == "__main__":
    print("=" * 60)
    print("TEST 1: Text-only pipeline (Diabetes)")
    print("=" * 60)
    r1 = get_ayurvedic_assessment(
        disease="Diabetes",
        symptoms="Frequent urination, fatigue, increased thirst",
        age_group="Middle-aged (40-60)", gender="Male",
        medical_history="Family history of diabetes",
        current_medications="Metformin",
        stress_levels="High",
        dietary_habits="High sugar, Low fiber"
    )
    print(r1)

    print("\n" + "=" * 60)
    print("TEST 2: Vision pipeline (Tongue image)")
    print("=" * 60)
    try:
        from PIL import Image
        img = Image.open("dataset/tongue_samples/kapha_tongue.jpg")
        r2 = get_ayurvedic_assessment(
            disease="General Checkup",
            symptoms="Fatigue, bloating, low energy",
            age_group="Adult (20-40)", gender="Female",
            tongue_image=img
        )
        print(r2)
    except FileNotFoundError:
        print("No tongue image found — run the dataset download command first.")
