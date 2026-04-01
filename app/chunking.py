from typing import List, Dict


def chunk_segments(
    segments: List[Dict],
    chunk_size: int = 1200,
    overlap: int = 200
) -> List[Dict]:

    chunks = []
    chunk_id = 0

    for segment in segments:
        text = segment["text"]
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]

            chunks.append({
                "chunk_id": chunk_id,
                "speaker_name": segment["speaker_name"],
                "speaker_role": segment["speaker_role"],
                "section_type": segment["section_type"],
                "text": chunk_text
            })

            chunk_id += 1
            start += chunk_size - overlap

    return chunks