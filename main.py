import requests
import json
import subprocess
import sys
import re

from datetime import datetime

# ==========================================
# CONFIGURATION
# ==========================================

API_BASE_URL = "http://localhost:1234"
REPORT_FILE = "report.json"
TEMP_FILE = "temp_code.py"

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
        "text": "Write ONLY Python code (no explanations, no markdown, no comments). Check if a string is a valid IPv4 address."
    },
    {
        "name": "move_zeros",
        "text": "Write ONLY Python code (no explanations, no markdown, no comments). Move all zeros to the end, keeping other numbers in original order."
    },
    {
        "name": "first_non_repeating_character",
        "text": "Write ONLY Python code (no explanations, no markdown, no comments). Find the first non-repeating character in a string and return its index. Return -1 if none exist."
    },
    {
        "name": "factorial_loop",
        "text": "Write ONLY Python code (no explanations, no markdown, no comments). Calculate the factorial of a number using a loop, without using recursion or the math module."
    },
    {
        "name": "extract_emails_regex",
        "text": "Write ONLY Python code (no explanations, no markdown, no comments). Use the 're' module to extract all valid email addresses from a block of text."
    },
    {
        "name": "calculate_exact_age",
        "text": "Write ONLY Python code (no explanations, no markdown, no comments). Take a birthdate string like 'YYYY-MM-DD' and calculate the person's exact age in years as of today."
    },
    {
        "name": "filter_adults_to_json",
        "text": "Write ONLY Python code (no explanations, no markdown, no comments). Take a list of Python dictionaries representing users, filter out anyone under 18, and write the remaining data to a JSON file."
    },
    {
        "name": "total_log_file_size",
        "text": "Write ONLY Python code (no explanations, no markdown, no comments). Take a directory path and return the total size (in bytes) of all '.log' files in that folder and its subfolders."
    },
    {
        "name": "shopping_cart_class",
        "text": "Write ONLY Python code (no explanations, no markdown, no comments). Create a 'ShoppingCart' class with methods to add an item with a price, remove an item by name, and calculate the total cost including a 5% tax."
    },
    {
        "name": "requests_retry_fetch",
        "text": "Write ONLY Python code (no explanations, no markdown, no comments). Use the 'requests' library to fetch data from 'https://api.example.com/data'. Retry up to 3 times with a 1-second delay before failing."
    },
    {
        "name": "robust_calculator",
        "text": "Write ONLY Python code (no explanations, no markdown, no comments). Create a robust calculator function that takes a math expression as a string. Use try/except to catch DivisionByZero and ValueError without crashing."
    },
    {
        "name": "reverse_string_no_slice",
        "text": "Write ONLY Python code (no explanations, no markdown, no comments). Reverse a string without using slice notation [::-1] or the reversed() function."
    },
    {
        "name": "fibonacci_pipe_format",
        "text": "Write ONLY Python code (no explanations, no markdown, no comments). Generate the Fibonacci sequence up to 100. Output must be a single string where numbers are separated by a pipe character '|' with no spaces."
    },
    {
        "name": "sort_descending_no_sorted",
        "text": "Write ONLY Python code (no explanations, no markdown, no comments). Sort a list of numbers from highest to lowest without using .sort() method or sorted() function."
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

    while True:
        try:
            choice = int(input("\nSelect model number: "))
            if 1 <= choice <= len(MODELS):
                return MODELS[choice - 1]
            
            print("Invalid number.")
        except ValueError:
            print("Enter a valid number.")

def load_model(model):
    print(f"\nLoading model: {model['display_name']}")

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/models/load",
            json={
                "model": model["api_name"]
            },
            timeout=60
        )

        if response.status_code == 200:
            print("Status Code:", response.status_code)
            print("Model loaded successfully.\n")
            return True

        print("Status Code:", response.status_code)
        print("Failed to load model.")
        print(response.text)
        return False

    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        return False

def unload_model():
    print("\nUnloading currently loaded models...")

    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/models",
            timeout=30
        )

        data = response.json()

        models = data.get("data", data.get("models", []))

        unloaded_any = False

        for model in models:
            for instance in model.get("loaded_instances", []):

                instance_id = instance["id"]

                requests.post(
                    f"{API_BASE_URL}/api/v1/models/unload",
                    json={"instance_id": instance_id},
                    timeout=30
                )

                print(f"Unloaded instance: {instance_id}")
                unloaded_any = True

        if not unloaded_any:
            print("No model was loaded.")

    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")

    except Exception as e:
        print(f"Unload failed: {e}")


def choose_prompt():
    print("Available Prompts:\n")

    for i, prompt in enumerate(PROMPTS, start=1):
        print(f"{i}. {prompt['name']}")

    while True:
        try:
            choice = int(input("\nSelect prompt number: "))

            if 1 <= choice <= len(PROMPTS):
                return PROMPTS[choice - 1]

            print("Invalid number.")

        except ValueError:
            print("Enter a valid number.")


def generate_output(prompt_text):
    print("\nGenerating output...\n")

    try:
        response = requests.post(
            f"{API_BASE_URL}/v1/completions",
            json={
                "prompt": prompt_text,
                "max_tokens": 200,
                "temperature": 0.7
            },
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        if (
            "choices" not in data
            or not data["choices"]
            or "text" not in data["choices"][0]
        ):
            print("Unexpected API response format.")
            return ""

        return data["choices"][0]["text"].strip()

    except requests.exceptions.RequestException as e:
        print(f"Generation failed: {e}")
        return ""

    except ValueError:
        print("Server returned invalid JSON.")
        return ""

    except Exception as e:
        print(f"Unexpected error: {e}")
        return ""
    

def load_existing_report():
    try:

        with open(
            REPORT_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            data = json.load(f)

        if not isinstance(data, list):
            return []

        return data

    except FileNotFoundError:
        return []

    except json.JSONDecodeError:
        print("report.json is corrupted.")
        return []

    except Exception as e:
        print(f"Error loading report: {e}")
        return []
    
    
def run_generated_code(code):
    try:

        code_blocks = re.findall(
            r"```(?:python)?\n(.*?)\n```",
            code,
            re.DOTALL
        )

        extracted_code = code_blocks[0] if code_blocks else code

        with open(
            TEMP_FILE,
            "w",
            encoding="utf-8"
        ) as f:
            f.write(extracted_code)

        result = subprocess.run(
            [sys.executable, TEMP_FILE],
            capture_output=True,
            text=True,
            timeout=10
        )

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }

    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": "Execution timed out.",
            "return_code": -1
        }

    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "return_code": -1
        }

def save_to_report(prompt, model, output, execution_result):
    data = load_existing_report()

    logs = (
        f"STDOUT:\n{execution_result['stdout']}"
        f"\n\nSTDERR:\n{execution_result['stderr']}"
    )

    data.append({
        "prompt_name": prompt["name"],
        "model_name": model["display_name"],
        "model_api_name": model["api_name"],
        "prompt_text": prompt["text"],
        "output": output,
        "logs": logs,
        "return_code": execution_result["return_code"],
        "timestamp": datetime.now().isoformat()
    })

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )

    print("✓ Result saved to report.json")



def choose_from_report():
    data = load_existing_report()

    if not data:
        print("\nNo saved results in report.json")
        return None

    print("\nSaved Test Results:\n")

    for i, result in enumerate(data, start=1):
        print(
            f"{i}. "
            f"{result['prompt_name']} | "
            f"{result['model_name']} | "
            f"{result['timestamp']}"
        )

    while True:
        try:
            choice = int(input("\nSelect result number: "))

            if 1 <= choice <= len(data):
                return data[choice - 1]

            print("Invalid number.")

        except ValueError:
            print("Enter a valid number.")



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
        print("3. Start Test (Generate & Execute Code)")
        print("4. Exit")

        try:
            choice = int(input("\nEnter your choice: "))
        except ValueError:
            print("\nEnter a valid number.")
            continue

        if choice == 1:
            # Select and load a model
            current_model = choose_model()
            load_model(current_model)

        elif choice == 2:
            # Unload the current model
            unload_model()
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

            # Show generated code
            print("\nGenerated Output:\n")
            print(output)

            # Run the generated code
            print("\nRunning generated code...\n")
            execution_result = run_generated_code(output)

            # Show execution results
            print("Execution Results:")
            print("Return Code:", execution_result["return_code"])
            print("\nStandard Output:")
            print(execution_result["stdout"])
            print("\nErrors:")
            print(execution_result["stderr"])

            # Save everything to report.json
            save_to_report(
                selected_prompt,
                current_model,
                output,
                execution_result
            )

            print("\nResult added to report.json")
            print("Testing complete.")

        elif choice == 4:
            print("\nExiting program...")
            sys.exit()

        else:
            print("\nInvalid choice. Please try again.")

startup()