import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3:latest"


def build_summary_prompt(context):
    return f"""
You are a long-term investor like Warren Buffett.

Summarize this earnings call into:

1. Business Performance
2. Growth Drivers
3. Risks
4. Management Quality (tone, confidence)
5. Investment Insight (Buy / Watch / Risky)

Rules:
- Be concise
- No hallucination
- Think like an investor, not analyst

Context:
{context}

Summary:
"""


def generate_investor_summary(chunks):
    context = ""

    for c in chunks[:10]:  # limit context
        context += c["text"] + "\n\n"

    prompt = build_summary_prompt(context)

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

    if response.status_code != 200:
        raise Exception(f"Ollama API Error: {response.text}")

    return response.json()["response"]