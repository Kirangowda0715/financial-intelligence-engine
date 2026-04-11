import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3:latest"

def build_advanced_summary_prompt(context):
    return f"""
You are a senior fundamental analyst.
Generate a highly actionable executive summary based on the provided earnings call transcript.

Sections required:
1. Key Highlights (Bullet points)
2. Growth Drivers (Bullet points)
3. Risks (Bullet points)
4. Outlook (Brief summary)
5. Business Thesis

For "Business Thesis", assess:
- Business quality
- Execution of strategy
- Fundamental upside vs downside risks
Synthesize the thesis clearly with evidence. Do not give trading advice.

Rule: Limit the entire response to approximately 200 words. Keep it strictly focused and actionable. Do not hallucinate.

Context:
{context}

Response Format Strategy:
Use clear markdown headings (##) for the sections.
"""

def generate_advanced_summary(chunks):
    context = ""
    for c in chunks[:12]:
        context += c["text"] + "\n\n"

    prompt = build_advanced_summary_prompt(context)

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
