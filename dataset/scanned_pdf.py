import json
from pdf2image import convert_from_path
import pytesseract
from transformers import AutoProcessor, AutoModelForImageTextToText
import torch
from pathlib import Path

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
PDF_PATH = "pricelist.pdf"
PROMPT_PATH = "prompts/dataset.txt"
OUTPUT_PATH = "output/output.json"
MODEL_ID = "google/medgemma-1.5-4b-it"

DEVICE = "cpu"   # change to "cuda" if you have GPU

# --------------------------------------------------
# Load prompt (relative path)
# --------------------------------------------------
prompt_file = Path(PROMPT_PATH)
if not prompt_file.exists():
    raise FileNotFoundError(f"Prompt file not found: {PROMPT_PATH}")

with open(prompt_file, "r", encoding="utf-8") as f:
    base_prompt = f.read().strip()

# --------------------------------------------------
# Load MedGemma (official Google model)
# --------------------------------------------------
processor = AutoProcessor.from_pretrained(MODEL_ID)
model = AutoModelForImageTextToText.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float32,
    device_map=DEVICE
)
model.eval()

# --------------------------------------------------
# Convert PDF → images
# --------------------------------------------------
images = convert_from_path(PDF_PATH)

results = []

# --------------------------------------------------
# Process each page
# --------------------------------------------------
for page_index, image in enumerate(images, start=1):
    # OCR text (optional, for traceability/debugging)
    ocr_text = pytesseract.image_to_string(image)

    # Build final prompt
    prompt = f"""
{base_prompt}

OCR_TEXT:
{ocr_text}
"""

    # Prepare inputs for MedGemma
    inputs = processor(
        images=image,
        text=prompt,
        return_tensors="pt"
    )

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,
            do_sample=False,
            temperature=0.0
        )

    response_text = processor.batch_decode(
        outputs,
        skip_special_tokens=True
    )[0]

    results.append({
        "page": page_index,
        "extracted_data": response_text
    })

# --------------------------------------------------
# Save output
# --------------------------------------------------
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4, ensure_ascii=False)

print("✅ PDF processed with MedGemma successfully")
