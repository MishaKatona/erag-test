from gen_positive_pairs import gen_and_save_positive_pairs_from_ocr_dict
from ocr_extraction import extract_text_as_pages
import os
import json
from pathlib import Path


# document_name = "Fundamental_Concepts_Liquid_Rocket_Engines"
document_name = "Handbook_Space_Technology"
# document_name = "Liquid_Rocket_Lines_Bellows_Hoses_Filters"
# document_name = "Rocket_Propulsion_Elements"

# check if it has already been ocred
if not os.path.exists(f"ocr_output/{document_name}.json"):
    pages = extract_text_as_pages(document_name)
else:
    print(f"OCR already done for {document_name} - Skipping")
    with open(f"ocr_output/{document_name}.json", "r") as f:
        pages = json.load(f)

# check if positive pairs have already been generated
if not Path(f"positive_pairs/{document_name}_pairs.json").is_file():
    print("does not exist")
    gen_and_save_positive_pairs_from_ocr_dict(
        pages, f"positive_pairs/{document_name}_pairs")
else:
    print(f"Positive pairs already generated for {document_name}")

