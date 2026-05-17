import requests
import json

prompt = "Write a Python function to print a pattern of stars in the shape of a pyramid with a given number of levels."

response = requests.post(
    "http://localhost:1234/v1/completions",
    json={
        "prompt": prompt,
        "max_tokens": 200,
        "temperature": 0.7
    }
)

text = response.json()["choices"][0]["text"].strip()

print("Generated Code:\n")
print(text)

with open("report.json", "w") as f:
    json.dump({
        "prompt": prompt,
        "generated_code": text
    }, f, indent=2)

print("\nSaved to report.json")