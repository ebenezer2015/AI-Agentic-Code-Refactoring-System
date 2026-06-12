import sys
import os
import difflib
from langgraph.graph import StateGraph, END

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from state import AgentState
from agent_coder import coder_agent_node
from agent_tester import tester_agent_node
from agent_guardrail import guardrail_agent_node

def generate_diff_node(state: AgentState) -> dict:
    """Compares original and final code to generate a clean Git-style markdown diff."""
    orig_lines = state["original_code"].splitlines(keepends=True)
    new_lines = state["current_code"].splitlines(keepends=True)
    
    # Calculate unified diff lines
    diff = difflib.unified_diff(
        orig_lines, 
        new_lines, 
        fromfile="Original Legacy Code", 
        tofile="Optimized Agent Code"
    )
    
    diff_text = "".join(diff)
    if not diff_text.strip():
        diff_text = "No changes were required. The original code was already optimal."
        
    return {"code_diff": diff_text}

def router_conditional_logic(state: AgentState):
    if state["iterations"] >= 3:
        return "diff_generator"
    if not state["test_results"] or not state["test_results"]["success"]:
        return "coder"
    if not state["guardrail_passed"]:
        return "coder"
    return "diff_generator"

# Build updated Graph Architecture
workflow = StateGraph(AgentState)
workflow.add_node("coder", coder_agent_node)
workflow.add_node("tester", tester_agent_node)
workflow.add_node("guardrail", guardrail_agent_node)
workflow.add_node("diff_generator", generate_diff_node) # NEW: Diff generator node

# Connect pipeline paths
workflow.set_entry_point("coder")
workflow.add_edge("coder", "tester")
workflow.add_edge("tester", "guardrail")

# Use conditional routing to point to the diff node instead of stopping instantly
workflow.add_conditional_edges(
    "guardrail",
    router_conditional_logic,
    {"coder": "coder", "diff_generator": "diff_generator"}
)

# Connect diff engine to terminal exit point
workflow.add_edge("diff_generator", END)

refactor_engine = workflow.compile()
