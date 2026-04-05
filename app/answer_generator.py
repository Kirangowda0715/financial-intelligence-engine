import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3:latest"


def build_context(chunks):
    if not chunks:
        return "No context available."

    context = ""
    for i, c in enumerate(chunks):
        m = c.get("metadata", {})
        context += f"""
[Source {i+1}]
Speaker: {m.get('speaker_name', 'Unknown')}
Role: {m.get('speaker_role', 'Unknown')}
Section: {m.get('section_type', 'Unknown')}

Content:
{c.get('text', '')}

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
- If data is missing in the context, say "Not mentioned"
- Always cite sources like [Source 1]

Query:
{query}

Context:
{context}

Answer:
"""


def call_ollama(prompt):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=180
        )

        if response.status_code != 200:
            raise Exception(f"Ollama returned HTTP {response.status_code}: {response.text[:300]}")

        data = response.json()
        answer = data.get("response", "").strip()
        if not answer:
            raise Exception("Ollama returned an empty response.")
        return answer

    except requests.exceptions.ConnectionError:
        raise Exception(
            "Cannot connect to Ollama at localhost:11434. "
            "Please make sure Ollama is running: open a terminal and run 'ollama serve'."
        )
    except requests.exceptions.Timeout:
        raise Exception(
            "Ollama timed out after 180 seconds. "
            "The model may be too busy or the query context is too large."
        )


def generate_answer(query, retrieved_chunks):
    context = build_context(retrieved_chunks)
    prompt = build_prompt(query, context)
    return call_ollama(prompt)