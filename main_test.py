import requests
import json
from datetime import datetime

# ==========================================
# LITELM FORGE - MODEL TEST SYSTEM
# ==========================================

MODELS = [
    {
        "display_name": "Qwen 2.5 Coder 1.5B",
        "api_name": "qwen2.5-coder-1.5b-instruct"
    },
    {
        "display_name": "StarCoder2 3B",
        "api_name": "starcoder2-3b"
    },
    {
        "display_name": "Llama 3.2 3B Instruct",
        "api_name": "llama-3.2-3b-instruct"
    },
    {
        "display_name": "Qwen 2.5 Coder 3B",
        "api_name": "qwen2.5-coder-3b-instruct"
    }
]

PROMPTS = [
    {
        "name": "valid_ipv4",
        "text": "Write a Python function to check if a string is a valid IPv4 address."
    },
    {
        "name": "move_zeros",
        "text": "Write a function that takes a list of integers and moves all zeros to the end, keeping the other numbers in their original order."
    },
    {
        "name": "first_non_repeating_character",
        "text": "Write a function to find the first non-repeating character in a string and return its index. If none exist, return -1."
    },
    {
        "name": "factorial_loop",
        "text": "Write a function to calculate the factorial of a number using a loop, without using recursion or the math module."
    },
    {
        "name": "extract_emails_regex",
        "text": "Write a Python script using the 're' module to extract all valid email addresses from a giant block of text."
    },
    {
        "name": "calculate_exact_age",
        "text": "Write a function that takes a birthdate string like 'YYYY-MM-DD' and calculates the person's exact age in years as of today."
    },
    {
        "name": "filter_adults_to_json",
        "text": "Write a script that takes a list of Python dictionaries representing users, filters out anyone under 18, and writes the remaining data to a JSON file."
    },
    {
        "name": "total_log_file_size",
        "text": "Write a function that takes a directory path and returns the total size (in bytes) of all '.log' files in that folder and its subfolders."
    },
    {
        "name": "shopping_cart_class",
        "text": "Create a 'ShoppingCart' class. It needs methods to add an item with a price, remove an item by name, and calculate the total cost including a 5% tax."
    },
    {
        "name": "requests_retry_fetch",
        "text": "Write a function using the 'requests' library to fetch data from 'https://api.example.com/data'. If the server returns an error, retry up to 3 times with a 1-second delay before failing."
    },
    {
        "name": "robust_calculator",
        "text": "Write a robust calculator function that takes a math expression as a string (like '10 / 2'). It must safely use try/except blocks to catch DivisionByZero and ValueError without crashing."
    },
    {
        "name": "reverse_string_no_slice",
        "text": "Write a Python function to reverse a string, but you are STRICTLY FORBIDDEN from using Python's slice notation [::-1] or the built-in reversed() function."
    },
    {
        "name": "fibonacci_pipe_format",
        "text": "Write a script to generate the Fibonacci sequence up to 100. The output MUST be a single string where numbers are separated by a pipe character '|' and no spaces."
    },
    {
        "name": "sort_descending_no_sorted",
        "text": "Write a function that sorts a list of numbers from highest to lowest, but do not use the built-in .sort() method or sorted() function."
    }
]


# ==========================================
# FUNCTIONS
# ==========================================

def show_title():
    print("=" * 50)
    print("        WELCOME TO MODEL TEST")
    print("=" * 50)


def choose_model():
    print("\nAvailable Models:\n")

    for i, model in enumerate(MODELS, start=1):
        print(f"{i}. {model['display_name']}")

    choice = int(input("\nSelect model number: "))
    return MODELS[choice - 1]


def load_model(model):
    print(f"\nLoading model: {model['display_name']}")

    response = requests.post(
        "http://localhost:1234/api/v1/models/load",
        json={
            "model": model["api_name"]
        }
    )

    print("Status Code:", response.status_code)
    print("Model loaded successfully.\n")


def choose_prompt():
    print("Available Prompts:\n")

    for i, prompt in enumerate(PROMPTS, start=1):
        print(f"{i}. {prompt['name']}")

    choice = int(input("\nSelect prompt number: "))
    return PROMPTS[choice - 1]


def generate_output(prompt_text):
    print("\nGenerating output...\n")

    response = requests.post(
        "http://localhost:1234/v1/completions",
        json={
            "prompt": prompt_text,
            "max_tokens": 200,
            "temperature": 0.7
        }
    )

    return response.json()["choices"][0]["text"].strip()


def load_existing_report():
    try:
        with open("report.json", "r") as f:
            data = json.load(f)

        if not isinstance(data, list):
            data = []

    except:
        data = []

    return data


def save_to_report(prompt, model, output):
    data = load_existing_report()

    data.append({
        "prompt_name": prompt["name"],
        "model_name": model["display_name"],
        "prompt_text": prompt["text"],
        "output": output,
        "timestamp": datetime.now().isoformat()
    })

    with open("report.json", "w") as f:
        json.dump(data, f, indent=2)

import sys

# ==========================================
# STARTUP FUNCTIONS
# ==========================================

def unload_current_model():
    """Unload all currently loaded models"""
    print("\nUnloading currently loaded models...")

    try:
        response = requests.get("http://localhost:1234/api/v1/models")
        data = response.json()

        models = data.get("data", data.get("models", []))
        unloaded_any = False

        for model in models:
            for instance in model.get("loaded_instances", []):
                instance_id = instance["id"]

                requests.post(
                    "http://localhost:1234/api/v1/models/unload",
                    json={"instance_id": instance_id}
                )

                print(f"Unloaded instance: {instance_id}")
                unloaded_any = True

        if not unloaded_any:
            print("No model was loaded.")

    except Exception as e:
        print("Error while unloading model:", e)


def load_model(model):
    """Load the selected model"""
    print(f"\nLoading model: {model['display_name']}")

    response = requests.post(
        "http://localhost:1234/api/v1/models/load",
        json={
            "model": model["api_name"]
        }
    )

    print("Status Code:", response.status_code)
    print("Model loaded successfully.\n")


def startup():
    """Main menu loop"""
    current_model = None  # remembers the currently loaded model

    while True:
        print("\n" + "=" * 50)
        print("        WELCOME TO MODEL TEST")
        print("=" * 50)

        if current_model:
            print(f"\nCurrent Model: {current_model['display_name']}")
        else:
            print("\nCurrent Model: None")

        print("\n1. Load Model")
        print("2. Unload Model")
        print("3. Start Test")
        print("4. Exit")

        choice = int(input("\nEnter your choice: "))

        if choice == 1:
            # Select and load a model
            unload_current_model()
            current_model = choose_model()
            load_model(current_model)

        elif choice == 2:
            # Unload the current model
            unload_current_model()
            current_model = None

        elif choice == 3:
            # Start test directly using already loaded model
            if current_model is None:
                print("\nNo model loaded.")
                print("Please use option 1 to load a model first.")
                continue

            # Select prompt
            selected_prompt = choose_prompt()

            # Generate output
            output = generate_output(selected_prompt["text"])

            # Show output
            print("\nGenerated Output:\n")
            print(output)

            # Save to report.json
            save_to_report(selected_prompt, current_model, output)

            print("\nResult added to report.json")
            print("Testing complete.")

        elif choice == 4:
            print("\nExiting program...")
            sys.exit()

        else:
            print("\nInvalid choice. Please try again.")
            
startup()