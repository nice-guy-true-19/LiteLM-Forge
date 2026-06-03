import requests
import json
import re
from datetime import datetime

# ==========================================
# CONFIGURATION
# ==========================================

JUDGE_MODELS = {
    "1": {"display_name": "Qwen 2.5 7B Instruct", "api_name": "qwen2.5-7b-instruct"},
    "2": {"display_name": "Llama 2 7B Chat", "api_name": "llama-2-7b-chat"},
    "3": {"display_name": "Mistral 7B Instruct", "api_name": "mistral-7b-instruct"},
}

REPORT_FILE = "litelm_forge_report.json"
ANALYSIS_FILE = "litelm_forge_analysis.json"

# ==========================================
# JSON PARSING - ROBUST
# ==========================================

def extract_json_from_text(text):
    """Extract JSON from text - multiple strategies"""
    if not text or not isinstance(text, str):
        return None
    
    # Strategy 1: Find {...} pattern
    json_patterns = [
        r'\{[\s\S]*\}',
        r'\{\s*".*?\}',
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
    
    # Strategy 2: Try whole text
    try:
        cleaned = text.strip()
        if cleaned.startswith('{') and cleaned.endswith('}'):
            return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    
    return None

# ==========================================
# ANALYSIS FILE MANAGEMENT
# ==========================================

def load_analysis_file():
    """Load existing analysis or create new"""
    try:
        with open(ANALYSIS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "analyses" in data:
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    
    return {
        "created": datetime.now().isoformat(),
        "judge_model": None,
        "analyses": [],
        "summary": {
            "total_analyzed": 0,
            "avg_score": 0.0,
            "pass_rate": 0.0,
            "by_prompt": {},
            "by_model": {}
        }
    }

def save_analysis_file(data):
    """Save analysis to JSON"""
    with open(ANALYSIS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def update_summary(analyses):
    """Calculate summary statistics"""
    if not analyses:
        return {
            "total_analyzed": 0,
            "avg_score": 0.0,
            "pass_rate": 0.0,
            "by_prompt": {},
            "by_model": {}
        }
    
    total = len(analyses)
    passed = sum(1 for a in analyses if a.get("passed", False))
    scores = [a.get("overall_score", 0) for a in analyses if a.get("overall_score")]
    avg_score = sum(scores) / len(scores) if scores else 0
    
    # By prompt
    by_prompt = {}
    for a in analyses:
        prompt = a.get("prompt_name", "unknown")
        if prompt not in by_prompt:
            by_prompt[prompt] = {"count": 0, "avg_score": 0}
        by_prompt[prompt]["count"] += 1
    
    for prompt in by_prompt:
        prompt_analyses = [a for a in analyses if a.get("prompt_name") == prompt]
        scores = [a.get("overall_score", 0) for a in prompt_analyses if a.get("overall_score")]
        by_prompt[prompt]["avg_score"] = round(sum(scores) / len(scores), 2) if scores else 0
    
    # By model
    by_model = {}
    for a in analyses:
        model = a.get("model_name", "unknown")
        if model not in by_model:
            by_model[model] = {"count": 0, "avg_score": 0}
        by_model[model]["count"] += 1
    
    for model in by_model:
        model_analyses = [a for a in analyses if a.get("model_name") == model]
        scores = [a.get("overall_score", 0) for a in model_analyses if a.get("overall_score")]
        by_model[model]["avg_score"] = round(sum(scores) / len(scores), 2) if scores else 0
    
    return {
        "total_analyzed": total,
        "avg_score": round(avg_score, 2),
        "pass_rate": round((passed / total) * 100, 2),
        "by_prompt": by_prompt,
        "by_model": by_model
    }

# ==========================================
# DEDUPLICATION
# ==========================================

def already_analyzed(report_index):
    """Check if result already analyzed"""
    data = load_analysis_file()
    return any(a.get("report_index") == report_index for a in data["analyses"])

def find_duplicates(analyses):
    """Find results with multiple analyses"""
    indices = [a.get("report_index") for a in analyses]
    return [i for i in set(indices) if indices.count(i) > 1]

# ==========================================
# SMART TOKEN CALCULATION
# ==========================================

def calculate_tokens_needed(entry):
    """Intelligently calculate tokens based on code size"""
    code = entry.get("output", "")
    prompt = entry.get("prompt_text", "")
    
    # Estimate: 1 token ≈ 4 chars
    code_tokens = len(code) // 4
    prompt_tokens = len(prompt) // 4
    
    # Minimum response size
    min_response = 200
    
    # Total needed
    total_needed = code_tokens + prompt_tokens + min_response
    
    # Add 10% buffer
    final_tokens = int(total_needed * 1.1)
    
    # Cap between limits
    return max(300, min(final_tokens, 600))

# ==========================================
# JUDGE MODEL MANAGEMENT
# ==========================================

def choose_judge_model():
    """Select judge model"""
    print("\n🧠 Available Judge Models:\n")
    for key, model in JUDGE_MODELS.items():
        print(f"{key}. {model['display_name']}")
    
    while True:
        choice = input("\nSelect model (1-3): ").strip()
        if choice in JUDGE_MODELS:
            return JUDGE_MODELS[choice]
        print("❌ Invalid choice")

def load_judge_model(model):
    """Load judge model in LM Studio"""
    print(f"\n🔄 Loading: {model['display_name']}")
    
    try:
        response = requests.post(
            "http://localhost:1234/api/v1/models/load",
            json={"model": model["api_name"]},
            timeout=300
        )
        
        if response.status_code == 200:
            print("✅ Judge model loaded")
            return True
        else:
            print(f"❌ Failed (HTTP {response.status_code})")
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False

def unload_judge_model(model):
    """Unload judge model"""
    print(f"\n🔄 Unloading: {model['display_name']}")
    
    try:
        response = requests.post(
            "http://localhost:1234/api/v1/models/unload",
            json={"model": model["api_name"]},
            timeout=300
        )
        print("✅ Unload complete")
    except Exception as e:
        print(f"⚠️  Warning: {e}")

# ==========================================
# ANALYSIS PROMPT - FAST & SMART
# ==========================================

def create_analysis_prompt(entry):
    """Create fast analysis prompt"""
    prompt = f"""Analyze this code. Return ONLY JSON (no markdown, no text):

TASK: {entry.get("prompt_name", "unknown")}
MODEL: {entry.get("model_name", "unknown")}

PROMPT: {entry.get("prompt_text", "")[:200]}

CODE OUTPUT:
{entry.get("output", "")[:300]}

EXECUTION: Return code {entry.get("return_code")}
Errors: {str(entry.get("logs", ""))[:150]}

Rate 1-10: How well solves the task?
Pass: true/false - Runs without errors?

RESPOND WITH ONLY THIS JSON:
{{
  "overall_score": <1-10>,
  "passed": <true/false>,
  "issues": ["issue1", "issue2"],
  "strengths": ["strength1"],
  "verdict": "one sentence"
}}"""
    return prompt.strip()

# ==========================================
# ANALYSIS EXECUTION
# ==========================================

def analyze_entry(entry, judge_model):
    """Run analysis on single entry"""
    try:
        prompt = create_analysis_prompt(entry)
        max_tokens = calculate_tokens_needed(entry)
        
        response = requests.post(
            "http://localhost:1234/v1/completions",
            json={
                "model": judge_model["api_name"],
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": 0.2
            },
            timeout=120
        )
        
        response.raise_for_status()
        data = response.json()
        
        if "choices" not in data or not data["choices"]:
            return None
        
        text = data["choices"][0].get("text", "").strip()
        
        if not text:
            return None
        
        # Extract JSON
        analysis = extract_json_from_text(text)
        
        if analysis and isinstance(analysis, dict) and "overall_score" in analysis:
            return analysis
        
        return None
    
    except requests.exceptions.Timeout:
        return None
    except Exception:
        return None

# ==========================================
# REPORT LOADING & FILTERING
# ==========================================

def load_report():
    """Load main test report"""
    try:
        with open(REPORT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "sessions" in data:
            return data
    except:
        pass
    return {"sessions": []}

def get_all_results():
    """Get all test results from report"""
    report = load_report()
    results = []
    
    for session in report.get("sessions", []):
        for result in session.get("results", []):
            results.append(result)
    
    return results

# ==========================================
# MAIN MENU
# ==========================================

def show_menu():
    """Display menu"""
    print("\n" + "=" * 55)
    print("    🔬 LITELM FORGE - CODE ANALYSIS & JUDGING")
    print("=" * 55)

def analyze_single(judge_model, all_results):
    """Analyze single result"""
    if not all_results:
        print("❌ No test results found")
        return
    
    print(f"\n📊 Available Results ({len(all_results)} total):\n")
    
    for i, result in enumerate(all_results[:20]):  # Show first 20
        prompt = result.get("prompt_name", "?")
        model = result.get("model_name", "?")
        status = "✅" if result.get("passed") else "❌"
        print(f"{i}: {status} {prompt} ({model})")
    
    if len(all_results) > 20:
        print(f"... and {len(all_results) - 20} more")
    
    while True:
        try:
            idx = int(input("\nSelect index (or -1 to cancel): "))
            if idx == -1:
                return
            if 0 <= idx < len(all_results):
                break
            print(f"❌ Enter 0-{len(all_results)-1}")
        except ValueError:
            print("❌ Invalid input")
    
    result = all_results[idx]
    
    if already_analyzed(idx):
        print("⚠️  Already analyzed. Analyze again? (y/n): ", end="")
        if input().lower() != "y":
            return
    
    print("\n🔄 Analyzing...")
    analysis = analyze_entry(result, judge_model)
    
    if not analysis:
        print("❌ Analysis failed or parse error")
        return
    
    # Save
    data = load_analysis_file()
    data["judge_model"] = judge_model["display_name"]
    data["analyses"].append({
        "report_index": idx,
        "prompt_name": result.get("prompt_name"),
        "model_name": result.get("model_name"),
        "timestamp": datetime.now().isoformat(),
        **analysis
    })
    data["summary"] = update_summary(data["analyses"])
    save_analysis_file(data)
    
    print(f"\n✅ Score: {analysis.get('overall_score', '?')}/10")
    print(f"✅ Passed: {analysis.get('passed', False)}")
    print(f"💡 Verdict: {analysis.get('verdict', 'N/A')}")
    print("✅ Saved")

def analyze_bulk(judge_model):
    """Analyze multiple results"""
    all_results = get_all_results()
    
    if not all_results:
        print("❌ No test results found")
        return
    
    print("\n📊 Bulk Analysis Menu:\n")
    print("1️⃣  Analyze ALL unanalyzed results")
    print("2️⃣  Analyze from selected prompts")
    print("3️⃣  Analyze from selected models")
    print("4️⃣  Back")
    
    choice = input("\nChoice: ").strip()
    
    if choice == "1":
        results_to_analyze = [
            r for i, r in enumerate(all_results) 
            if not already_analyzed(i)
        ]
        if not results_to_analyze:
            print("✅ All results already analyzed!")
            return
    
    elif choice == "2":
        prompts = sorted(list(set(r.get("prompt_name", "unknown") for r in all_results)))
        print("\n📝 Available Prompts:\n")
        for i, p in enumerate(prompts, 1):
            count = len([r for r in all_results if r.get("prompt_name") == p])
            print(f"{i}. {p} ({count} results)")
        
        while True:
            try:
                p_choice = int(input("\nSelect prompt: ").strip())
                if 1 <= p_choice <= len(prompts):
                    selected_prompt = prompts[p_choice - 1]
                    results_to_analyze = [
                        r for i, r in enumerate(all_results)
                        if r.get("prompt_name") == selected_prompt and not already_analyzed(i)
                    ]
                    break
                print(f"❌ Enter 1-{len(prompts)}")
            except ValueError:
                print("❌ Invalid input")
        
        if not results_to_analyze:
            print("✅ All results for this prompt already analyzed!")
            return
    
    elif choice == "3":
        models = sorted(list(set(r.get("model_name", "unknown") for r in all_results)))
        print("\n🤖 Available Models:\n")
        for i, m in enumerate(models, 1):
            count = len([r for r in all_results if r.get("model_name") == m])
            print(f"{i}. {m} ({count} results)")
        
        while True:
            try:
                m_choice = int(input("\nSelect model: ").strip())
                if 1 <= m_choice <= len(models):
                    selected_model = models[m_choice - 1]
                    results_to_analyze = [
                        r for i, r in enumerate(all_results)
                        if r.get("model_name") == selected_model and not already_analyzed(i)
                    ]
                    break
                print(f"❌ Enter 1-{len(models)}")
            except ValueError:
                print("❌ Invalid input")
        
        if not results_to_analyze:
            print("✅ All results for this model already analyzed!")
            return
    
    else:
        return
    
    # Confirm
    print(f"\n📊 Found {len(results_to_analyze)} result(s) to analyze")
    confirm = input("Start analysis? (y/n): ").strip().lower()
    if confirm != "y":
        return
    
    # Run bulk
    data = load_analysis_file()
    data["judge_model"] = judge_model["display_name"]
    
    passed = 0
    failed = 0
    
    for i, result in enumerate(results_to_analyze, 1):
        prompt = result.get("prompt_name", "?")
        model = result.get("model_name", "?")
        print(f"[{i}/{len(results_to_analyze)}] {prompt} ({model})...", end=" ", flush=True)
        
        analysis = analyze_entry(result, judge_model)
        
        if analysis and isinstance(analysis, dict) and "overall_score" in analysis:
            all_results_idx = all_results.index(result)
            data["analyses"].append({
                "report_index": all_results_idx,
                "prompt_name": result.get("prompt_name"),
                "model_name": result.get("model_name"),
                "timestamp": datetime.now().isoformat(),
                **analysis
            })
            score = analysis.get("overall_score", "?")
            status = "✅" if analysis.get("passed") else "⚠️"
            print(f"{status} ({score}/10)")
            passed += 1
        else:
            print("⏭️  (skipped)")
            failed += 1
    
    data["summary"] = update_summary(data["analyses"])
    save_analysis_file(data)
    
    print(f"\n{'='*55}")
    print(f"✅ Complete! {passed}/{len(results_to_analyze)} analyzed")
    if failed > 0:
        print(f"⏭️  {failed} skipped (parse errors)")
    print(f"📊 Total in DB: {data['summary']['total_analyzed']}")
    print(f"📈 Avg score: {data['summary']['avg_score']}/10")
    print(f"✅ Pass rate: {data['summary']['pass_rate']}%")

def view_analysis():
    """View existing analysis"""
    data = load_analysis_file()
    
    if not data["analyses"]:
        print("❌ No analyses yet")
        return
    
    summary = data["summary"]
    
    print(f"\n📊 Analysis Summary")
    print(f"   Total analyzed: {summary['total_analyzed']}")
    print(f"   Avg score: {summary['avg_score']}/10")
    print(f"   Pass rate: {summary['pass_rate']}%")
    
    if summary["by_prompt"]:
        print(f"\n📝 By Prompt:")
        for prompt, stats in sorted(summary["by_prompt"].items()):
            print(f"   {prompt}: {stats['avg_score']}/10 ({stats['count']})")
    
    if summary["by_model"]:
        print(f"\n🤖 By Model:")
        for model, stats in sorted(summary["by_model"].items()):
            print(f"   {model}: {stats['avg_score']}/10 ({stats['count']})")
    
    print(f"\n💾 File: {ANALYSIS_FILE}")

def remove_duplicates():
    """Remove duplicate analyses"""
    data = load_analysis_file()
    duplicates = find_duplicates(data["analyses"])
    
    if not duplicates:
        print("✅ No duplicates")
        return
    
    print(f"⚠️  Found {len(duplicates)} duplicate(s)")
    
    seen = set()
    unique = []
    for a in data["analyses"]:
        idx = a.get("report_index")
        if idx not in seen:
            unique.append(a)
            seen.add(idx)
    
    data["analyses"] = unique
    data["summary"] = update_summary(unique)
    save_analysis_file(data)
    
    print(f"✅ Cleaned! {len(unique)} unique analyses")

# ==========================================
# MAIN LOOP
# ==========================================

def main():
    """Main loop"""
    judge_model = None
    
    while True:
        show_menu()
        
        if judge_model:
            print(f"\n🧠 Judge: {judge_model['display_name']}")
        else:
            print("\n🧠 Judge: None")
        
        print("\n1️⃣  Select Judge Model")
        print("2️⃣  Analyze Single")
        print("3️⃣  Bulk Analyze")
        print("4️⃣  View Results")
        print("5️⃣  Remove Duplicates")
        print("6️⃣  Exit")
        
        try:
            choice = input("\nChoice: ").strip()
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        
        if choice == "1":
            judge_model = choose_judge_model()
            if load_judge_model(judge_model):
                print("✅ Ready to analyze")
        
        elif choice == "2":
            if not judge_model:
                print("❌ Select judge model first")
            else:
                all_results = get_all_results()
                analyze_single(judge_model, all_results)
        
        elif choice == "3":
            if not judge_model:
                print("❌ Select judge model first")
            else:
                analyze_bulk(judge_model)
        
        elif choice == "4":
            view_analysis()
        
        elif choice == "5":
            remove_duplicates()
        
        elif choice == "6":
            if judge_model:
                unload_judge_model(judge_model)
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()