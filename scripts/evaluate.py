import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import torch
from inference import get_ayurvedic_assessment
import pandas as pd

print("Running evaluation on held-out test cases...")

df = pd.read_csv("dataset/kaggle_ayurveda/AyurGenixAI_Dataset.csv")
df = df.fillna("Not specified")

# Take last 10 rows as test cases
test_cases = df.tail(10)

results = []
for _, row in test_cases.iterrows():
    prediction = get_ayurvedic_assessment(
        disease=row["Disease"],
        symptoms=row["Symptoms"],
        age_group=row["Age Group"],
        gender=row["Gender"],
        medical_history=row["Medical History"],
        current_medications=row["Current Medications"],
        stress_levels=row["Stress Levels"],
        dietary_habits=row["Dietary Habits"]
    )

    # Check if correct herbs mentioned
    expected_herbs = str(row["Ayurvedic Herbs"]).lower()
    predicted_lower = prediction.lower()

    herb_list = [h.strip() for h in expected_herbs.split(",")]
    herbs_found = sum(1 for h in herb_list if h in predicted_lower)
    herb_accuracy = herbs_found / len(herb_list) if herb_list else 0

    results.append({
        "disease": row["Disease"],
        "expected_herbs": row["Ayurvedic Herbs"],
        "herb_accuracy": herb_accuracy,
        "prediction_length": len(prediction)
    })

    print(f"Disease: {row['Disease']}")
    print(f"Expected herbs: {row['Ayurvedic Herbs']}")
    print(f"Herb accuracy: {herb_accuracy:.0%}")
    print("-" * 40)

avg_accuracy = sum(r["herb_accuracy"] for r in results) / len(results)
print(f"\nOverall herb recommendation accuracy: {avg_accuracy:.0%}")
print(f"Total test cases: {len(results)}")
print("\nSave these numbers for your writeup!")
