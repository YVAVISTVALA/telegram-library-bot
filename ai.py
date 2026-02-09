import requests
from config import HF_API_KEY

API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-small"

headers = {
    "Authorization": f"Bearer {HF_API_KEY}"
}

def ask_ai(prompt):
    payload = {"inputs": prompt[:300]}
    r = requests.post(API_URL, headers=headers, json=payload, timeout=30)

    if r.status_code != 200:
        return "AI is busy. Try later."

    data = r.json()
    return data[0]["generated_text"][:1000]
