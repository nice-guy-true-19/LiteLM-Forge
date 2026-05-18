import requests

# List of available models
MODELS = [
    "qwen2.5-coder-1.5b-instruct",
    "qwen2.5-coder-3b-instruct",
    "qwen2.5-coder-7b-instruct"
]

# Show menu
print("Select a model:\n")

for i, model in enumerate(MODELS, start=1):
    print(f"{i}. {model}")

# Get user choice
choice = int(input("\nEnter model number: "))

# Convert menu number to list index
selected_model = MODELS[choice - 1]

print(f"\nLoading: {selected_model}")

# Load model through LM Studio API
response = requests.post(
    "http://localhost:1234/api/v1/models/load",
    json={
        "model": selected_model
    }
)

print("\nStatus Code:", response.status_code)
print("Response:", response.text)