import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3:latest"

def build_metrics_prompt(context):
    return f"""
You are an AI financial data extractor.
Extract key financial metrics from the provided transcript.

CRITICAL INSTRUCTION: Output RAW JSON ONLY. Do NOT wrap the JSON in ```json blocks. Do NOT output any conversational text.

Look for:
- Revenue growth %
- EBITDA or margins
- Explicit Guidance
- Segment performance

If not mentioned, leave the string empty ("") or array empty ([]).

JSON Format:
{{
  "revenue_growth": "string",
  "margin": "string",
  "guidance": "string",
  "segments": ["segment 1 performance", "segment 2 performance"]
}}

Context:
{context}
"""

def extract_financial_metrics(chunks):
    context = ""
    for c in chunks[:20]:
        context += c["text"] + "\n\n"

    prompt = build_metrics_prompt(context)

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
    
    # Safely parse and unwrap the JSON
    parsed_data = {}
    try:
        data = json.loads(text_resp)
        # Unwrap if LLM wrapped in {"metrics": {...}}
        if isinstance(data, dict):
            if "metrics" in data and isinstance(data["metrics"], dict):
                parsed_data = data["metrics"]
            elif "financial_metrics" in data and isinstance(data["financial_metrics"], dict):
                parsed_data = data["financial_metrics"]
            else:
                parsed_data = data
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', text_resp, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                parsed_data = data.get("metrics", data)
            except:
                pass
    
    # Ensure all required keys exist
    return {
        "revenue_growth": parsed_data.get("revenue_growth", parsed_data.get("Revenue Growth", "")),
        "margin": parsed_data.get("margin", parsed_data.get("Margin", "")),
        "guidance": parsed_data.get("guidance", parsed_data.get("Guidance", "")),
        "segments": parsed_data.get("segments", parsed_data.get("Segments", []))
    }
