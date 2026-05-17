import requests
import json
from datetime import datetime

PROMPT_NAME = "loops"
MODEL_NAME = "Qwen 2.5 Coder 1.5B"
PROMPT_TEXT = "Write a Python function to reverse a string using loops ."

response = requests.post(
    "http://localhost:1234/v1/completions",
    json={
        "prompt": PROMPT_TEXT,
        "max_tokens": 200,
        "temperature": 0.7
    }
)

output = response.json()["choices"][0]["text"].strip()

try:
    with open("report.json", "r") as f:
        data = json.load(f)

    if not isinstance(data, list):
        data = []

except:
    data = []

data.append({
    "prompt_name": PROMPT_NAME,
    "model_name": MODEL_NAME,
    "prompt_text": PROMPT_TEXT,
    "output": output,
    "timestamp": datetime.now().isoformat()
})

with open("report.json", "w") as f:
    json.dump(data, f, indent=2)

print(output)
print("Result added to report.json")