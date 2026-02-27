import re
from typing import List, Dict


def is_speaker_line(line: str) -> bool:
    line = line.strip()

    if len(line) == 0:
        return False

    if len(line) > 120:
        return False

    if "-" in line or ":" in line:
        word_count = len(line.split())
        if 2 <= word_count <= 12:
            return True

    return False


def detect_role(line: str) -> str:
    lower_line = line.lower()

    if "ceo" in lower_line:
        return "CEO"
    if "cfo" in lower_line:
        return "CFO"
    if "analyst" in lower_line:
        return "Analyst"
    if "operator" in lower_line:
        return "Operator"

    return "Management"


def parse_transcript_structure(full_text: str) -> List[Dict]:
    lines = full_text.split("\n")

    segments = []
    current_speaker = None
    current_role = None
    current_section = "Prepared Remarks"
    current_text = []

    char_index = 0

    for line in lines:
        stripped = line.strip()

        # Detect Q&A section start
        if "question" in stripped.lower() or "q&a" in stripped.lower():
            current_section = "Q&A"

        if is_speaker_line(stripped):
            # Save previous segment
            if current_speaker and current_text:
                segments.append({
                    "speaker_name": current_speaker,
                    "speaker_role": current_role,
                    "section_type": current_section,
                    "text": " ".join(current_text)
                })

            # Start new segment
            current_speaker = stripped
            current_role = detect_role(stripped)
            current_text = []

        else:
            if stripped:
                current_text.append(stripped)

        char_index += len(line) + 1

    # Save last segment
    if current_speaker and current_text:
        segments.append({
            "speaker_name": current_speaker,
            "speaker_role": current_role,
            "section_type": current_section,
            "text": " ".join(current_text)
        })

    return segments