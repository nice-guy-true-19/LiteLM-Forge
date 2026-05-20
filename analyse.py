import requests
import json

# =========================
# Configuration
# =========================

JUDGE_MODEL = {
    "display_name": "Qwen 2.5 7B Instruct",
    "api_name": "qwen2.5-7b-instruct"
}


# =========================
# Model Management
# =========================

def load_model(model):
    print(f"\nLoading model: {model['display_name']}")

    response = requests.post(
        "http://localhost:1234/api/v1/models/load",
        json={
            "model": model["api_name"]
        },
        timeout=300
    )

    print(response.text)

    if response.status_code != 200:
        raise RuntimeError(f"Failed to load model: {response.text}")

    print("Model loaded successfully.")


def unload_model(model):
    print(f"\nUnloading model: {model['display_name']}")

    response = requests.post(
        "http://localhost:1234/api/v1/models/unload",
        json={
            "model": model["api_name"]
        },
        timeout=300
    )

    print(response.text)

    if response.status_code != 200:
        print("Warning: unload may have failed.")

    print("Unload request completed.")


# =========================
# Load report.json
# =========================

with open("report.json", "r", encoding="utf-8") as f:
    results = json.load(f)

if not isinstance(results, list):
    raise RuntimeError("report.json must contain a list of results.")

if len(results) == 0:
    raise RuntimeError("report.json is empty.")


# =========================
# Ask Whether to Load Model
# =========================

print("\nModel loading:")
print("1. Load qwen2.5-7b-instruct")
print("2. Assume model is already loaded")

load_choice = input("Choose (1/2): ").strip()

if load_choice in ("1", "y", "Y", "yes", "YES", "Yes"):
    try:
        load_model(JUDGE_MODEL)
    except Exception as e:
        print("Could not load the model.")
        print("Reason:", e)
        raise
else:
    print("\nAssuming model is already loaded.")


# =========================
# Ask Whether to Unload Model
# =========================

print("\nModel management:")
print("1. Unload qwen2.5-7b-instruct after analysis")
print("2. Keep model loaded")

unload_choice = input("Choose (1/2): ").strip()


# =========================
# Show Available Entries
# =========================

print("\nAvailable entries in report.json:")
for i, entry in enumerate(results):
    prompt_name = entry.get("prompt_name", "unknown")
    model_name = entry.get("model_name", "unknown")
    print(f"{i}: {prompt_name} ({model_name})")


# =========================
# Choose Index to Analyze
# =========================

while True:
    try:
        INDEX = int(input("\nEnter the index to analyze: ").strip())
        if 0 <= INDEX < len(results):
            break
        else:
            print(f"Please enter a number between 0 and {len(results) - 1}.")
    except ValueError:
        print("Please enter a valid integer.")


# =========================
# Select Item
# =========================

item = results[INDEX]
code = item["output"]


# =========================
# Create Analysis Prompt
# =========================

prompt = f"""
You are a senior software engineer and security auditor.

Analyze the following AI-generated Python code and provide a professional review.

====================
TASK INFORMATION
====================
Prompt Name: {item["prompt_name"]}
Model Name: {item["model_name"]}

Original Prompt:
{item.get("prompt_text", "")}

====================
GENERATED CODE
====================
{item["output"]}

====================
EXECUTION RESULTS
====================
Return Code: {item.get("return_code")}
Logs:
{item.get("logs", "")}

====================
REVIEW CRITERIA
====================

1. Prompt Compliance
- Did the model follow instructions exactly?
- Did it output only Python code?
- Did it include explanations, markdown, or comments when forbidden?

2. Logic & Correctness
- Boundary conditions
- Off-by-one errors
- Empty inputs
- Zero/null handling
- Logic inversions
- Hallucinated APIs
- Unintended state mutations

3. Security & Data Flow
- Unsanitized inputs
- Hardcoded secrets
- Missing authorization checks

4. Structural Health & Code Smells
- Excessive nesting
- Duplicate code
- Dead code
- Unused variables
- Single responsibility principle

5. Error Handling & Resilience
- Bare except/catch blocks
- Missing await
- Resource leaks
- Silent failures

6. Runtime Execution
- Did the code execute successfully?
- If not, explain the exact failure.

7. Performance
- Time complexity
- Memory usage
- Unnecessary operations

8. Readability & Maintainability
- Naming quality
- Clarity
- Simplicity

====================
OUTPUT FORMAT
====================

Overall Score: X/10

Prompt Compliance:
...

Logic & Correctness:
...

Security:
...

Structural Health:
...

Error Handling:
...

Runtime Execution:
...

Performance:
...

Readability:
...

Key Strengths:
- ...
- ...

Key Weaknesses:
- ...
- ...

Final Verdict:
...
"""


# =========================
# Send Prompt to LM Studio
# =========================

print("\nRunning analysis...")

response = requests.post(
    "http://localhost:1234/v1/completions",
    json={
        "model": JUDGE_MODEL["api_name"],
        "prompt": prompt,
        "max_tokens": 1200,
        "temperature": 0.3
    },
    timeout=600
)

data = response.json()


# =========================
# Extract Analysis Text
# =========================

if "choices" not in data:
    print("Unexpected API response:")
    print(json.dumps(data, indent=2))
    raise RuntimeError("API response does not contain 'choices'.")

choice = data["choices"][0]

if "text" in choice:
    analysis = choice["text"].strip()
elif "message" in choice and "content" in choice["message"]:
    analysis = choice["message"]["content"].strip()
else:
    print("Unexpected choice format:")
    print(json.dumps(choice, indent=2))
    raise RuntimeError("Could not extract analysis text.")


# =========================
# Load Existing analysis.json
# =========================

try:
    with open("analysis.json", "r", encoding="utf-8") as f:
        analyses = json.load(f)

    if not isinstance(analyses, list):
        analyses = []
except:
    analyses = []


# =========================
# Append New Analysis
# =========================

analyses.append({
    "index": INDEX,
    "prompt_name": item["prompt_name"],
    "model_name": item["model_name"],
    "judge_model": JUDGE_MODEL["api_name"],
    "prompt_text": item.get("prompt_text", ""),
    "return_code": item.get("return_code"),
    "logs": item.get("logs", ""),
    "timestamp": item.get("timestamp", ""),
    "analysis": analysis
})


# =========================
# Save analysis.json
# =========================

with open("analysis.json", "w", encoding="utf-8") as f:
    json.dump(analyses, f, indent=2, ensure_ascii=False)


# =========================
# Print Result
# =========================

print("\nAnalysis added to analysis.json")
print("\n" + "=" * 80)
print(analysis)
print("=" * 80)


# =========================
# Optionally Unload Model
# =========================

if unload_choice in ("1", "y", "Y", "yes", "YES", "Yes"):
    try:
        unload_model(JUDGE_MODEL)
    except Exception as e:
        print("\nCould not unload the model.")
        print("Reason:", e)
else:
    print("\nKeeping model loaded.")