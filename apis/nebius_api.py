import os
import requests
from dotenv import load_dotenv
import urllib.parse

# Load the .env file from the parent directory
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=env_path)

NEBIUS_API_KEY = os.getenv("NEBIUS_API_KEY")
NEBIUS_API_URL = "https://api.studio.nebius.ai/v1/chat/completions"

def generate_response(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {NEBIUS_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "meta-llama/Meta-Llama-3.1-70B-Instruct",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 150
    }
    try:
        response = requests.post(NEBIUS_API_URL, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        else:
            print("Nebius API error:", response.text)
            return ""
    except Exception as e:
        print("Error calling Nebius API:", e)
        return ""
