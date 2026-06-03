import requests
import json
import subprocess
import sys
import re
from datetime import datetime
from uuid import uuid4

# ==========================================
# CONFIGURATION
# ==========================================

API_BASE_URL = "http://localhost:1234"
REPORT_FILE = "litelm_forge_report.json"
TEMP_FILE = "temp_code.py"

# ==========================================
# MODELS & PROMPTS
# ==========================================

MODELS = [
    {"display_name": "Qwen 2.5 Coder 1.5B", "api_name": "qwen2.5-coder-1.5b-instruct"},
    {"display_name": "StarCoder2 3B", "api_name": "starcoder2-3b"},
    {"display_name": "Llama 3.2 3B Instruct", "api_name": "llama-3.2-3b-instruct"},
    {"display_name": "Qwen 2.5 Coder 3B", "api_name": "qwen2.5-coder-3b-instruct"},
]

PROMPTS = [
    {"name": "valid_ipv4", "text": "Write ONLY Python code (no explanations, no markdown, no comments). Check if a string is a valid IPv4 address."},
    {"name": "move_zeros", "text": "Write ONLY Python code (no explanations, no markdown, no comments). Move all zeros to the end, keeping other numbers in original order."},
    {"name": "first_non_repeating_character", "text": "Write ONLY Python code (no explanations, no markdown, no comments). Find the first non-repeating character in a string and return its index. Return -1 if none exist."},
    {"name": "factorial_loop", "text": "Write ONLY Python code (no explanations, no markdown, no comments). Calculate the factorial of a number using a loop, without using recursion or the math module."},
    {"name": "extract_emails_regex", "text": "Write ONLY Python code (no explanations, no markdown, no comments). Use the 're' module to extract all valid email addresses from a block of text."},
    {"name": "calculate_exact_age", "text": "Write ONLY Python code (no explanations, no markdown, no comments). Take a birthdate string like 'YYYY-MM-DD' and calculate the person's exact age in years as of today."},
    {"name": "filter_adults_to_json", "text": "Write ONLY Python code (no explanations, no markdown, no comments). Take a list of Python dictionaries representing users, filter out anyone under 18, and write the remaining data to a JSON file."},
    {"name": "total_log_file_size", "text": "Write ONLY Python code (no explanations, no markdown, no comments). Take a directory path and return the total size (in bytes) of all '.log' files in that folder and its subfolders."},
    {"name": "shopping_cart_class", "text": "Write ONLY Python code (no explanations, no markdown, no comments). Create a 'ShoppingCart' class with methods to add an item with a price, remove an item by name, and calculate the total cost including a 5% tax."},
    {"name": "requests_retry_fetch", "text": "Write ONLY Python code (no explanations, no markdown, no comments). Use the 'requests' library to fetch data from 'https://api.example.com/data'. Retry up to 3 times with a 1-second delay before failing."},
    {"name": "robust_calculator", "text": "Write ONLY Python code (no explanations, no markdown, no comments). Create a robust calculator function that takes a math expression as a string. Use try/except to catch DivisionByZero and ValueError without crashing."},
    {"name": "reverse_string_no_slice", "text": "Write ONLY Python code (no explanations, no markdown, no comments). Reverse a string without using slice notation [::-1] or the reversed() function."},
    {"name": "fibonacci_pipe_format", "text": "Write ONLY Python code (no explanations, no markdown, no comments). Generate the Fibonacci sequence up to 100. Output must be a single string where numbers are separated by a pipe character '|' with no spaces."},
    {"name": "sort_descending_no_sorted", "text": "Write ONLY Python code (no explanations, no markdown, no comments). Sort a list of numbers from highest to lowest without using .sort() method or sorted() function."},
]

# ==========================================
# REPORT MANAGEMENT
# ==========================================

def load_report():
    """Load existing report or create new one"""
    try:
        with open(REPORT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "sessions" in data:
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    
    return {
        "created": datetime.now().isoformat(),
        "sessions": []
    }

def save_report(report_data):
    """Save report to JSON file"""
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

def add_test_result(session_id, prompt, model, output, execution_result):
    """Add single test result to session"""
    report = load_report()
    
    # Find session
    session = next((s for s in report["sessions"] if s["session_id"] == session_id), None)
    if not session:
        return
    
    logs = f"STDOUT:\n{execution_result['stdout']}\n\nSTDERR:\n{execution_result['stderr']}"
    
    session["results"].append({
        "prompt_name": prompt["name"],
        "model_name": model["display_name"],
        "prompt_text": prompt["text"],
        "output": output,
        "logs": logs,
        "return_code": execution_result["return_code"],
        "passed": execution_result["return_code"] == 0,
        "timestamp": datetime.now().isoformat()
    })
    
    save_report(report)

def create_session(model):
    """Create new testing session"""
    session = {
        "session_id": datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + str(uuid4())[:8],
        "model_name": model["display_name"],
        "model_api_name": model["api_name"],
        "created": datetime.now().isoformat(),
        "results": []
    }
    
    report = load_report()
    report["sessions"].append(session)
    save_report(report)
    
    return session["session_id"]

# ==========================================
# CODE EXTRACTION & EXECUTION
# ==========================================

def extract_code(output):
    """Extract Python code from output - try multiple methods"""
    
    # Method 1: Extract code from markdown blocks
    code_blocks = re.findall(r"```(?:python)?\n(.*?)\n```", output, re.DOTALL)
    if code_blocks:
        return code_blocks[0].strip()
    
    # Method 2: Extract code from ```python ... ```
    code_blocks = re.findall(r"```python(.*?)```", output, re.DOTALL)
    if code_blocks:
        return code_blocks[0].strip()
    
    # Method 3: Look for lines starting with 'def ', 'class ', 'import ', etc.
    lines = output.split('\n')
    code_start = -1
    for i, line in enumerate(lines):
        if any(line.strip().startswith(kw) for kw in ['def ', 'class ', 'import ', 'from ', 'if ', 'for ', '[']):
            code_start = i
            break
    
    if code_start != -1:
        code_content = '\n'.join(lines[code_start:])
        # Remove trailing explanations
        if '\n\nExample' in code_content or '\n\nUsage' in code_content:
            code_content = code_content.split('\n\nExample')[0].split('\n\nUsage')[0]
        return code_content.strip()
    
    # Method 4: Return whole output if it looks like code
    if output.count('\n') > 2:
        return output.strip()
    
    return ""

def run_code(code):
    """Execute code and capture results"""
    try:
        extracted = extract_code(code)
        
        if not extracted:
            return {
                "stdout": "",
                "stderr": "Could not extract valid Python code from output",
                "return_code": -1
            }
        
        with open(TEMP_FILE, "w", encoding="utf-8") as f:
            f.write(extracted)
        
        result = subprocess.run(
            [sys.executable, TEMP_FILE],
            capture_output=True,
            text=True,
            timeout=40
        )
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }
    
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Execution timed out (>10s)", "return_code": -1}
    except Exception as e:
        return {"stdout": "", "stderr": str(e), "return_code": -1}

# ==========================================
# MODEL MANAGEMENT
# ==========================================

def choose_model():
    """Select a model from list"""
    print("\n📦 Available Models:\n")
    for i, model in enumerate(MODELS, 1):
        print(f"{i}. {model['display_name']}")
    
    while True:
        try:
            choice = int(input("\nSelect model (number): "))
            if 1 <= choice <= len(MODELS):
                return MODELS[choice - 1]
            print(f"❌ Enter number 1-{len(MODELS)}")
        except ValueError:
            print("❌ Invalid input")

def load_model(model):
    """Load model in LM Studio"""
    print(f"\n🔄 Loading: {model['display_name']}")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/models/load",
            json={"model": model["api_name"]},
            timeout=60
        )
        
        if response.status_code == 200:
            print("✅ Model loaded successfully")
            return True
        else:
            print(f"❌ Load failed (HTTP {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False

def unload_model():
    """Unload all models"""
    print("\n🔄 Unloading models...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/models", timeout=30)
        data = response.json()
        models = data.get("data", data.get("models", []))
        
        unloaded = 0
        for model in models:
            for instance in model.get("loaded_instances", []):
                requests.post(
                    f"{API_BASE_URL}/api/v1/models/unload",
                    json={"instance_id": instance["id"]},
                    timeout=30
                )
                unloaded += 1
        
        if unloaded > 0:
            print(f"✅ Unloaded {unloaded} instance(s)")
        else:
            print("ℹ️  No models were loaded")
    except Exception as e:
        print(f"❌ Error: {e}")

# ==========================================
# GENERATION
# ==========================================

def generate(prompt_text):
    """Generate code from prompt"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/v1/completions",
            json={"prompt": prompt_text, "max_tokens": 300, "temperature": 0.7},
            timeout=120
        )
        
        response.raise_for_status()
        data = response.json()
        
        if "choices" in data and data["choices"] and "text" in data["choices"][0]:
            return data["choices"][0]["text"].strip()
        else:
            print("❌ Unexpected API response")
            return ""
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Generation failed: {e}")
        return ""
    except Exception as e:
        print(f"❌ Error: {e}")
        return ""

# ==========================================
# PROMPTS
# ==========================================

def choose_prompt():
    """Select a prompt"""
    print("\n📝 Available Prompts:\n")
    for i, prompt in enumerate(PROMPTS, 1):
        print(f"{i}. {prompt['name']}")
    
    while True:
        try:
            choice = int(input("\nSelect prompt (number): "))
            if 1 <= choice <= len(PROMPTS):
                return PROMPTS[choice - 1]
            print(f"❌ Enter number 1-{len(PROMPTS)}")
        except ValueError:
            print("❌ Invalid input")

# ==========================================
# MAIN MENU
# ==========================================

def show_menu():
    """Display main menu"""
    print("\n" + "=" * 50)
    print("    ⚡ LITELM FORGE - TEST & BENCHMARK")
    print("=" * 50)

def single_prompt_test(model, session_id):
    """Run single prompt test"""
    prompt = choose_prompt()
    
    print(f"\n🔄 Generating code for: {prompt['name']}")
    output = generate(prompt["text"])
    
    if not output:
        print("❌ Generation failed")
        return
    
    print("\n📄 Generated Output:\n")
    print(output[:500] + ("..." if len(output) > 500 else ""))
    
    print("\n⚙️  Running code...")
    exec_result = run_code(output)
    
    print(f"\nReturn Code: {exec_result['return_code']}")
    print(f"STDOUT:\n{exec_result['stdout'][:200]}")
    if exec_result['stderr']:
        print(f"STDERR:\n{exec_result['stderr'][:200]}")
    
    add_test_result(session_id, prompt, model, output, exec_result)
    print("✅ Result saved to report")

def run_all_prompts(model, session_id):
    """Run all prompts (benchmark)"""
    report = load_report()
    session = next(s for s in report["sessions"] if s["session_id"] == session_id)
    
    total = len(PROMPTS)
    passed = 0
    
    print(f"\n🚀 Running {total} prompts...\n")
    
    for i, prompt in enumerate(PROMPTS, 1):
        print(f"[{i}/{total}] {prompt['name']}...", end=" ", flush=True)
        
        output = generate(prompt["text"])
        if not output:
            print("❌ Gen failed")
            continue
        
        exec_result = run_code(output)
        if exec_result["return_code"] == 0:
            passed += 1
            print("✅")
        else:
            print("❌")
        
        add_test_result(session_id, prompt, model, output, exec_result)
    
    # Update session summary
    report = load_report()
    session = next(s for s in report["sessions"] if s["session_id"] == session_id)
    session["summary"] = {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "success_rate": round((passed / total) * 100, 2)
    }
    save_report(report)
    
    print(f"\n✅ Benchmark complete! ({passed}/{total} passed, {round((passed/total)*100, 1)}%)")

def custom_prompt_test(model, session_id):
    """Run custom prompt"""
    print("\n📝 Enter your custom prompt:")
    prompt_text = input("> ").strip()
    
    if not prompt_text:
        print("❌ Empty prompt")
        return
    
    print(f"\n🔄 Generating...")
    output = generate(prompt_text)
    
    if not output:
        print("❌ Generation failed")
        return
    
    print("\n📄 Output:\n")
    print(output)
    
    print("\n⚙️  Running code...")
    exec_result = run_code(output)
    
    print(f"\nReturn Code: {exec_result['return_code']}")
    print(f"STDOUT:\n{exec_result['stdout']}")
    if exec_result['stderr']:
        print(f"STDERR:\n{exec_result['stderr']}")
    
    custom = {"name": "custom", "text": prompt_text}
    add_test_result(session_id, custom, model, output, exec_result)
    print("✅ Saved to report")

# ==========================================
# STARTUP
# ==========================================

def main():
    """Main loop"""
    current_model = None
    current_session = None
    
    while True:
        show_menu()
        
        if current_model:
            print(f"\n🔷 Model: {current_model['display_name']}")
        else:
            print("\n🔷 Model: None")
        
        print("\n1️⃣  Load Model")
        print("2️⃣  Unload Model")
        print("3️⃣  Single Test")
        print("4️⃣  Run All (Benchmark)")
        print("5️⃣  Custom Prompt")
        print("6️⃣  View Report")
        print("7️⃣  Exit")
        
        try:
            choice = input("\nChoice: ").strip()
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        
        if choice == "1":
            current_model = choose_model()
            if load_model(current_model):
                current_session = create_session(current_model)
                print(f"📌 Session: {current_session}")
        
        elif choice == "2":
            unload_model()
            current_model = None
        
        elif choice == "3":
            if not current_model:
                print("❌ Load a model first")
            else:
                single_prompt_test(current_model, current_session)
        
        elif choice == "4":
            if not current_model:
                print("❌ Load a model first")
            else:
                run_all_prompts(current_model, current_session)
        
        elif choice == "5":
            if not current_model:
                print("❌ Load a model first")
            else:
                custom_prompt_test(current_model, current_session)
        
        elif choice == "6":
            report = load_report()
            print(f"\n📊 Total Sessions: {len(report['sessions'])}")
            for session in report["sessions"][-5:]:  # Show last 5
                summary = session.get("summary", {})
                print(f"\n  {session['session_id']}")
                print(f"    Model: {session['model_name']}")
                if summary:
                    print(f"    Results: {summary.get('passed', 0)}/{summary.get('total', 0)}")
            print(f"\n📄 Full report: {REPORT_FILE}")
        
        elif choice == "7":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()