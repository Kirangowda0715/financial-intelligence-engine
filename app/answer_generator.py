import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3:latest"


def build_context(chunks):
    context = ""

    for i, c in enumerate(chunks):
        m = c["metadata"]

        context += f"""
[Source {i+1}]
Speaker: {m.get('speaker_name')}
Role: {m.get('speaker_role')}
Section: {m.get('section_type')}

Content:
{c['text']}

---
"""
    return context


def build_prompt(query, context):
    return f"""
You are a senior equity research analyst.

Analyze the query using ONLY the provided context.

Provide structured output:

1. Key Insights
2. Management Commentary
3. Key Drivers
4. Risks / Concerns
5. Analyst Perspective

Rules:
- Be concise and sharp
- Do NOT hallucinate
- If data missing, say "Not mentioned"
- Always cite sources like [Source 1]

Query:
{query}

Context:
{context}

Answer:
"""


def call_ollama(prompt):
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


def generate_answer(query, retrieved_chunks):
    context = build_context(retrieved_chunks)
    prompt = build_prompt(query, context)

    return call_ollama(prompt)