from typing import List, Dict


def is_speaker_line(line: str) -> bool:
    if len(line) == 0 or len(line) > 120:
        return False

    if ("-" in line or ":" in line) and 2 <= len(line.split()) <= 12:
        return True

    return False


def detect_role(line: str) -> str:
    l = line.lower()

    if "ceo" in l:
        return "CEO"
    if "cfo" in l:
        return "CFO"
    if "analyst" in l:
        return "Analyst"
    if "operator" in l:
        return "Operator"

    return "Management"


def parse_transcript_structure(full_text: str) -> List[Dict]:
    lines = full_text.split("\n")

    segments = []
    current_speaker = None
    current_role = None
    current_section = "Prepared Remarks"
    current_text = []

    for line in lines:
        stripped = line.strip()

        if "q&a" in stripped.lower() or "question and answer" in stripped.lower():
            current_section = "Q&A"

        if is_speaker_line(stripped):
            if current_speaker and current_text:
                segments.append({
                    "speaker_name": current_speaker,
                    "speaker_role": current_role,
                    "section_type": current_section,
                    "text": " ".join(current_text)
                })

            current_speaker = stripped
            current_role = detect_role(stripped)
            current_text = []

        else:
            if stripped:
                current_text.append(stripped)

    if current_speaker and current_text:
        segments.append({
            "speaker_name": current_speaker,
            "speaker_role": current_role,
            "section_type": current_section,
            "text": " ".join(current_text)
        })

    return segments