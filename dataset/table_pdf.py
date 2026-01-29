import json
import torch
from pathlib import Path

import pdfplumber
from transformers import AutoProcessor, AutoModelForImageTextToText

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
PDF_PATH = "pricelist.pdf"
PROMPT_PATH = "prompts/dataset.txt"
OUTPUT_PATH = "output.json"
MODEL_ID = "google/medgemma-1.5-4b-it"
DEVICE = "cpu"

# --------------------------------------------------
# Load prompt
# --------------------------------------------------
with open(PROMPT_PATH, "r", encoding="utf-8") as f:
    base_prompt = f.read().strip()

# --------------------------------------------------
# Load MedGemma
# --------------------------------------------------
processor = AutoProcessor.from_pretrained(MODEL_ID)
model = AutoModelForImageTextToText.from_pretrained(
    MODEL_ID,
    device_map=DEVICE,
    torch_dtype=torch.float32
)
model.eval()

results = []

# --------------------------------------------------
# Extract tables using pdfplumber
# --------------------------------------------------
with pdfplumber.open(PDF_PATH) as pdf:
    for page_idx, page in enumerate(pdf.pages, start=1):
        tables = page.extract_tables()

        for table_idx, table in enumerate(tables, start=1):
            # Convert table to text
            table_text = "\n".join(
                [" | ".join(cell or "" for cell in row) for row in table]
            )

            prompt = f"""
{base_prompt}

TABLE_DATA:
{table_text}
"""

            inputs = processor(
                text=prompt,
                return_tensors="pt"
            )

            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=700,
                    do_sample=False,
                    temperature=0.0
                )

            response_text = processor.batch_decode(
                outputs,
                skip_special_tokens=True
            )[0]

            results.append({
                "page": page_idx,
                "table": table_idx,
                "extracted_data": response_text
            })

# --------------------------------------------------
# Save output
# --------------------------------------------------
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4, ensure_ascii=False)

print("✅ Table data extracted successfully using MedGemma")
