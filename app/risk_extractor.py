import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3:latest"

def build_risk_prompt(context):
    return f"""
You are an AI risk analyst extracting financial and operational risks from earnings calls.

Given the transcript extract:
1. Key risks explicitly mentioned by management
2. Implicit risks based on tone and wording
3. New risks that appear novel

CRITICAL INSTRUCTION: Output RAW JSON ONLY. Do NOT wrap the JSON in ```json blocks. Do NOT output any conversational text.
Return an Array of Risk objects.

JSON Format:
[
  {{
    "risk_name": "string",
    "description": "string",
    "severity": "Low" | "Medium" | "High",
    "source_reference": "string quote"
  }}
]

Context:
{context}
"""

def extract_risks(chunks):
    context = ""
    for c in chunks[:15]:
        context += c["text"] + "\n\n"

    prompt = build_risk_prompt(context)

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "format": "json",
            "stream": False
        },
        timeout=120
    )

    if response.status_code != 200:
        raise Exception(f"Ollama API Error: {response.text}")

    text_resp = response.json()["response"]
    
    try:
        data = json.loads(text_resp)
        # Sometime LLM wraps in {"risks": [...]}
        if isinstance(data, dict):
            for key in ["risks", "risk", "extracted_risks", "Risk"]:
                if key in data and isinstance(data[key], list):
                    return data[key]
            # If no known key is found but it contains a lone array value
            for val in data.values():
                if isinstance(val, list):
                    return val
        elif isinstance(data, list):
            return data
    except json.JSONDecodeError:
        match = re.search(r'\[.*\]', text_resp, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                if isinstance(data, list):
                    return data
            except:
                pass
        
        # If it completely failed and outputted text, capture it as a single general risk
        if len(text_resp) > 20:
            return [{
                "risk_name": "General Risk Profile",
                "description": text_resp.strip(),
                "severity": "Medium",
                "source_reference": "Analyzed from text structure"
            }]
            
    return []
