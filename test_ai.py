import os
import requests

API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    print("❌ OPENROUTER_API_KEY not found in environment variables")
    exit()

url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "arcee-ai/trinity-large-preview:free",
    "messages": [
        {
            "role": "user",
            "content": "Explain in simple words: what is an unused EBS volume in AWS?"
        }
    ],
    "temperature": 0.3,
    "max_tokens": 150
}

try:
    response = requests.post(url, headers=headers, json=data, timeout=20)

    print("Status Code:", response.status_code)
    print()

    result = response.json()
    print("AI Response:\n")
    print(result["choices"][0]["message"]["content"])

except Exception as e:
    print("❌ Error calling OpenRouter:", str(e))