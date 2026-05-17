import requests
import json

# Load all generated code results
with open("report.json", "r") as f:
    results = json.load(f)

# Choose which entry to analyze
# 0 = first entry
# 1 = second entry
# 2 = third entry
INDEX = 0

# Select one item
item = results[INDEX]
code = item["output"]

# Create analysis prompt
prompt = f"""
Rate this Python code from 1 to 10.
Explain strengths and weaknesses.

Code:
{code}
"""

# Send to Qwen 7B running in LM Studio
response = requests.post(
    "http://localhost:1234/v1/completions",
    json={
        "prompt": prompt,
        "max_tokens": 300,
        "temperature": 0.3
    }
)

# Get analysis text
analysis = response.json()["choices"][0]["text"].strip()

# Load existing analyses if they exist
try:
    with open("analysis.json", "r") as f:
        analyses = json.load(f)

    if not isinstance(analyses, list):
        analyses = []
except:
    analyses = []

# Add new analysis
analyses.append({
    "index": INDEX,
    "prompt_name": item["prompt_name"],
    "model_name": item["model_name"],
    "analysis": analysis
})

# Save updated analysis list
with open("analysis.json", "w") as f:
    json.dump(analyses, f, indent=2)

print("Analysis added to analysis.json")
print(analysis)