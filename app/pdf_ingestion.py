import pdfplumber
from typing import Dict, List


MIN_CHAR_THRESHOLD_PER_PAGE = 50  # Used to detect scanned PDFs


def extract_pdf_content(file_path: str) -> Dict:
    pages_data: List[Dict] = []
    total_characters = 0

    with pdfplumber.open(file_path) as pdf:
        total_pages = len(pdf.pages)

        for i, page in enumerate(pdf.pages):
            raw_text = page.extract_text()

            if raw_text:
                cleaned_text = clean_text(raw_text)
                char_count = len(cleaned_text)
            else:
                cleaned_text = ""
                char_count = 0

            total_characters += char_count

            pages_data.append({
                "page_number": i + 1,
                "character_count": char_count,
                "text": cleaned_text
            })

    # Detect likely scanned PDF
    avg_chars_per_page = total_characters / total_pages if total_pages > 0 else 0

    if avg_chars_per_page < MIN_CHAR_THRESHOLD_PER_PAGE:
        raise ValueError("This appears to be a scanned PDF. Digital PDFs only supported in V1.")

    return {
        "total_pages": total_pages,
        "total_characters": total_characters,
        "average_characters_per_page": avg_chars_per_page,
        "pages": pages_data
    }


def clean_text(text: str) -> str:
    """
    Basic cleaning:
    - Strip extra spaces
    - Normalize line breaks
    """
    text = text.strip()
    text = text.replace("\r\n", "\n")
    text = "\n".join(line.strip() for line in text.split("\n"))
    return text