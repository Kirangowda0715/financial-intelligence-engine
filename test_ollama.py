import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={"model": "llama3:latest", "prompt": "hello", "stream": False}
)

print(response.status_code)
print(response.json())
