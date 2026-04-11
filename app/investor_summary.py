import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3:latest"


def build_summary_prompt(context):
    return f"""
You are a long-term investor analyzing businesses.

Provide a detailed and elaborate summary of this earnings call covering:

1. Business Performance (Extract exact financial numbers, revenue figures, and growth percentages if present)
2. Growth Drivers (Provide specific strategic initiatives)
3. Risks (Detail any concerns or headwinds)
4. Management Quality (Assess tone and confidence)
5. Business Outlook & Thesis

Rules:
- Be detailed and elaborate
- Extract accurate numbers for revenue and growth
- No hallucination
- Focus strictly on business fundamentals, do not give trading advice.

Context:
{context}

Detailed Summary:
"""


def generate_investor_summary(chunks):
    context = ""

    for c in chunks[:25]:  # limit context to first 25 chunks for more accurate data
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