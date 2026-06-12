import sys
import os
import nbformat
from nbconvert import PythonExporter

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from orchestrator import refactor_engine

def generate_markdown_report(filename: str, state: dict) -> str:
    """Formats diagnostic metadata, code diffs, and quality ratings into a markdown report."""
    initial_score = state.get("initial_quality_score", 0)
    final_score = state.get("final_quality_score", 0)
    score_improvement = final_score - initial_score
    
    report = f"# Code Optimization Diagnostic Report: {filename}\n\n"
    
    # NEW: Visual Code Quality Score Card Dashboard
    report += "## 📈 Code Quality Score Dashboard\n"
    report += "```text\n"
    report += f"Original Score: [{initial_score}/10] " + "⭐" * initial_score + "☆" * (10 - initial_score) + "\n"
    report += f"Optimized Score: [{final_score}/10] " + "⭐" * final_score + "☆" * (10 - final_score) + "\n"
    report += f"Net Improvement: +{score_improvement} Points\n"
    report += "```\n\n"
    
    report += "## 📊 Executive Summary\n"
    report += f"{state.get('change_summary', 'No summary provided.')}\n\n"
    
    report += "## 🔍 Code Line Modifications (Color-Coded Git-Style)\n"
    report += f"```diff\n{state.get('code_diff', 'No diff information recorded.')}\n```\n\n"
    
    report += "## 🐢 Identified Bottlenecks\n"
    bottlenecks = state.get("bottlenecks_identified", [])
    if bottlenecks:
        for b in bottlenecks: report += f"* **Bottleneck:** {b}\n"
    else: report += "* No critical structural bottlenecks flagged.\n"
    
    report += "\n## 🛡️ Handled Edge Cases & Security Defenses\n"
    edge_cases = state.get("edge_cases_addressed", [])
    if edge_cases:
        for ec in edge_cases: report += f"* **Resolved Risk:** {ec}\n"
    else: report += "* No hidden logical edge-case failures detected.\n"
    
    report += "\n## 📈 Execution Sandbox Metrics\n"
    test_res = state.get("test_results")
    if test_res and test_res.get("success"):
        report += "* **Sandbox Status:** Passed ✅\n"
        report += f"* **Runtime Sandbox Output:**\n```text\n{test_res.get('output', '').strip()}\n```\n"
    else:
        report += "* **Sandbox Status:** Failed or Skipped ❌\n"
        
    return report


def process_code_directory(input_dir: str, output_dir: str, custom_prompt: str = ""):
    input_path = os.path.abspath(input_dir)
    output_path = os.path.abspath(output_dir)
    
    if not os.path.exists(input_path):
        print(f"❌ Input folder '{input_dir}' not found.")
        return

    os.makedirs(output_path, exist_ok=True)
    
    all_files = os.listdir(input_path)
    files_to_process = [
        f for f in all_files 
        if f.endswith(".py") or f.endswith(".ipynb") or f.endswith(".sql")
    ]
    
    if not files_to_process:
        print(f"ℹ️ No active code files found inside '{input_dir}'.")
        return

    print(f"📂 Found {len(files_to_process)} file(s). Running engine...\n")

    for filename in files_to_process:
        src_file_path = os.path.join(input_path, filename)
        file_root, file_ext = os.path.splitext(filename)
        
        out_ext = ".sql" if file_ext.lower() == ".sql" else ".py"
        dest_code_path = os.path.join(output_path, f"optimized_{file_root}{out_ext}")
        dest_report_path = os.path.join(output_path, f"report_{file_root}.md")
        
        lang_mapping = {".py": "python", ".ipynb": "python", ".sql": "sql"}
        detected_lang = lang_mapping.get(file_ext.lower(), "python")

        print(f"🛠️  Processing: {filename} ({detected_lang.upper()})")
        
        try:
            if file_ext == ".ipynb":
                with open(src_file_path, "r", encoding="utf-8") as f:
                    notebook_content = nbformat.read(f, as_version=4)
                exporter = PythonExporter()
                source_code_string, _ = exporter.from_notebook_node(notebook_content)
            else:
                with open(src_file_path, "r", encoding="utf-8") as f:
                    source_code_string = f.read()

            # INJECT CUSTOM PROMPT: Passed safely into the LangGraph global state schema
            initial_state = {
                "original_code": source_code_string,
                "language": detected_lang,
                "current_code": source_code_string,
                "feedback_logs": [],
                "test_results": None,
                "guardrail_passed": False,
                "iterations": 0,
                "bottlenecks_identified": [],
                "edge_cases_addressed": [],
                "change_summary": "",
                "code_diff": "",
                "initial_quality_score": 0,
                "final_quality_score": 0,
                "custom_prompt": custom_prompt  # Ensured compatibility with state dictionary
            }

            final_state = refactor_engine.invoke(initial_state)
            
            with open(dest_code_path, "w", encoding="utf-8") as f_code:
                f_code.write(final_state["current_code"])
            
            markdown_report = generate_markdown_report(filename, final_state)
            with open(dest_report_path, "w", encoding="utf-8") as f_rep:
                f_rep.write(markdown_report)
                
            print(f"📋 [Done] Saved optimized code for {filename}\n")
            
        except Exception as e:
            print(f"❌ [Failed] Could not complete execution for {filename}: {str(e)}\n")

