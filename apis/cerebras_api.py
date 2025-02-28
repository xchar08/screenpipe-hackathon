import os
import requests

CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
CEREBRAS_API_URL = "https://api.cerebras.ai/v1/completions"

def generate_code(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {CEREBRAS_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": prompt,
        "max_tokens": 150,
        "model": "llama3.1-8b"
    }
    try:
        response = requests.post(CEREBRAS_API_URL, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            return result.get("choices", [{}])[0].get("text", "").strip()
        else:
            print("Cerebras API error:", response.text)
            return ""
    except Exception as e:
        print("Error calling Cerebras API:", e)
        return ""
