"""
parser.py - Extract raw text from lab result PDFs or plain text input.

Dependencies:
    pip install pdfplumber
"""

import pdfplumber
import re
from pathlib import Path


def parse_pdf(file_path: str) -> str:
    """
    Extract raw text from a PDF file.
    Returns a single string with all pages joined.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError("File must be a PDF")

    full_text = []

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text.append(text)

    return "\n".join(full_text)


def parse_text(raw_text: str) -> str:
    """
    Accept plain text input (e.g. pasted from a portal).
    Cleans up whitespace and returns normalized text.
    """
    # Normalize whitespace
    text = re.sub(r'\r\n', '\n', raw_text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    return text


def parse_input(file_path: str = None, raw_text: str = None) -> str:
    """
    Main entry point. Accepts either a PDF file path or raw pasted text.
    Returns normalized text ready for the marker extractor.
    """
    if file_path:
        return parse_pdf(file_path)
    elif raw_text:
        return parse_text(raw_text)
    else:
        raise ValueError("Must provide either file_path or raw_text")


def extract_report_metadata(text: str) -> dict:
    """
    Attempt to pull high-level metadata from the report text.
    Returns a dict with lab_name and report_date if found.
    """
    metadata = {
        "lab_name": None,
        "report_date": None,
    }

    # Common lab names
    lab_patterns = ["Quest Diagnostics", "LabCorp", "BioReference", "Sonora Quest"]
    for lab in lab_patterns:
        if lab.lower() in text.lower():
            metadata["lab_name"] = lab
            break

    # Date patterns: e.g. 01/15/2024, Jan 15 2024, 2024-01-15
    date_patterns = [
        r'\b(\d{1,2}/\d{1,2}/\d{4})\b',
        r'\b(\d{4}-\d{2}-\d{2})\b',
        r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4})\b',
    ]
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            metadata["report_date"] = match.group(1)
            break

    return metadata


# --- Quick test ---
if __name__ == "__main__":
    # Test with pasted text
    sample = """
    Quest Diagnostics
    Patient: John Doe
    Date: 01/15/2024

    COMPREHENSIVE METABOLIC PANEL
    Glucose         95      mg/dL     70-99
    BUN             14      mg/dL     7-25
    Creatinine      0.9     mg/dL     0.6-1.2
    Sodium          139     mmol/L    136-145
    """

    text = parse_input(raw_text=sample)
    print("--- Extracted Text ---")
    print(text)

    metadata = extract_report_metadata(text)
    print("\n--- Metadata ---")
    print(metadata)