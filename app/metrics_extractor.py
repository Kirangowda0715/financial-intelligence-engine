import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3:latest"

def build_metrics_prompt(context):
    return f"""
You are an AI financial data extractor.
Extract key financial metrics from the provided transcript.

Output structured JSON ONLY with no backticks, markdown, or conversational text. Look for:
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
    
    # Try parsing safely, fallback if format is broken
    try:
        return json.loads(text_resp)
    except json.JSONDecodeError:
        # Extract json using regex if LLM added markdown around it
        match = re.search(r'\{.*\}', text_resp, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                pass
    
    return {
        "revenue_growth": "",
        "margin": "",
        "guidance": "",
        "segments": []
    }
