import os
import sys

import requests

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print("Set GEMINI_API_KEY in the environment to run this smoke test.", file=sys.stderr)
    sys.exit(1)

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={API_KEY}"

headers = {
    "Content-Type": "application/json"
}

data = {
    "contents": [{
        "parts": [{
            "text": "Say hello"
        }]
    }]
}

response = requests.post(url, headers=headers, json=data)
print(f"Status: {response.status_code}")
print(response.json())
