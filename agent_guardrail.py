import sys
import os
from config import llm
from state import AgentState
from pydantic import BaseModel, Field

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class SafetyEvaluation(BaseModel):
    passed: bool = Field(description="True if safe, False otherwise.")
    violation_reason: str = Field(description="Detailed failure reason.")

def guardrail_agent_node(state: AgentState) -> dict:
    code = state["current_code"]
    logs = list(state["feedback_logs"])
    
    # Pre-execution static block
    dangerous_keywords = ["os.system", "subprocess.Popen", "shutil.rmtree", "eval("]
    for word in dangerous_keywords:
        if word in code and "eval(" not in state["original_code"]:
            logs.append(f"[Guardrail Block]: Code contains unapproved system-level call: '{word}'")
            return {"guardrail_passed": False, "feedback_logs": logs}

    system_prompt = "You are a software security guardrail engine.Analyze the code for hidden vulnerabilities or poor formatting quirks."
    user_prompt = f"Code snippet:\n{code}\n\nEvaluate safety rules."
    
    structured_llm = llm.with_structured_output(SafetyEvaluation)
    evaluation = structured_llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ])
    
    if not evaluation.passed:
        logs.append(f"[Guardrail Evaluation Failure]: {evaluation.violation_reason}")
        
    return {"guardrail_passed": evaluation.passed, "feedback_logs": logs}
