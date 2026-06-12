from pydantic import BaseModel, Field, field_validator
from typing import List
from config import llm
from state import AgentState

class CoderResponse(BaseModel):
    reasoning: str = Field(description="Internal technical justification.")
    refactored_code: str = Field(description="The raw executable optimized code block.")
    bottlenecks: List[str] = Field(description="Performance or structural problems found.")
    edge_cases: List[str] = Field(description="Edge cases or bugs addressed.")
    summary_of_changes: str = Field(description="Concise summary of changes.")
    # NEW: Quality metrics bounded strictly between 1 and 10
    initial_score: int = Field(description="Quality rating of the INPUT code on a scale of 1 to 10.")
    final_score: int = Field(description="Quality rating of the REFACTORED code on a scale of 1 to 10.")

    @field_validator('initial_score', 'final_score')
    @classmethod
    def validate_scores(cls, v: int) -> int:
        if not 1 <= v <= 10:
            raise ValueError('Scores must be strictly between 1 and 10')
        return v

def coder_agent_node(state: AgentState) -> dict:
    current_iteration = state["iterations"]
    
    system_prompt = (
        f"You are an expert software engineer and code quality inspector optimizing source files written in {state['language']}.\n"
        "Evaluate the code quality on a strict scale from 1 (broken/unreadable) to 10 (perfect clean-code architecture).\n"
        "Identify structural bottlenecks and edge cases, fix them, and provide an updated post-optimization score."
    )

    if current_iteration >= 2:
        system_prompt += (
            "\n\nCRITICAL BUDGET WARNING:\n"
            "Prior iterations failed verification checks. Apply a 'Micro-Patching' strategy."
        )

    processed_feedback = ""
    if state['feedback_logs']:
        processed_feedback = f"Immediate Failure To Fix:\n{state['feedback_logs'][-1]}"

    user_content = f"Original Code:\n{state['original_code']}\n\n"
    user_content += f"{processed_feedback}" if processed_feedback else f"Current Target Code:\n{state['current_code']}"

    structured_llm = llm.with_structured_output(CoderResponse)
    response = structured_llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ])
    
    # Track the original baseline score only on the very first loop iteration
    initial_score_tracked = state.get("initial_quality_score", 0)
    if current_iteration == 0:
        initial_score_tracked = response.initial_score

    return {
        "current_code": response.refactored_code,
        "iterations": current_iteration + 1,
        "bottlenecks_identified": response.bottlenecks,
        "edge_cases_addressed": response.edge_cases,
        "change_summary": response.summary_of_changes,
        "initial_quality_score": initial_score_tracked,
        "final_quality_score": response.final_score
    }














