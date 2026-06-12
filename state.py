import sys
import os
from typing import TypedDict, List, Optional

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class AgentState(TypedDict):
    original_code: str
    language: str
    current_code: str
    feedback_logs: List[str]
    test_results: Optional[dict]
    guardrail_passed: bool
    iterations: int
    bottlenecks_identified: List[str]
    edge_cases_addressed: List[str]
    change_summary: str
    # NEW: Holds the Git-style text diff analysis
    code_diff: str
    # NEW: Quality scoring metrics
    initial_quality_score: int
    final_quality_score: int



