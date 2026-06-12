#!/usr/bin/env python
# coding: utf-8

import concurrent.futures
import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pydantic import BaseModel, Field

# Configure logging for parallel thread visibility
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(threadName)s] %(levelname)s: %(message)s")

# ==========================================
# 1. ARCHITECTURAL WEIGHTS CONFIGURATION
# ==========================================
SCORING_WEIGHTS = {
    "rule_severity": 0.35,
    "link_analysis": 0.30,
    "customer_risk": 0.20,
    "historical_performance": 0.15
}

# ==========================================
# 2. IN-MEMORY METADATA (MOCK DATABASES)
# ==========================================
MOCK_RULES_DB = {
    "R1001": {"description": "Rapid Movement of Funds", "historical_exit_rate": 0.72},
    "R1002": {"description": "High Volume Cash Structuring", "historical_exit_rate": 0.88}
}

MOCK_CUSTOMER_DB = {
    "CUST_9981": {
        "name": "Alpha Taxi & Logistics",
        "industry": "Taxi / Transport Operations",
        "cash_intensity_score": 90,
        "jurisdiction_risk_score": 40,
        "previous_investigations": 2,
        "confirmed_sars": 1,
        "linked_exited_counterparties": 3
    },
    "CUST_1234": {
        "name": "Modern Retail Enterprises",
        "industry": "E-Commerce Consulting",
        "cash_intensity_score": 15,
        "jurisdiction_risk_score": 20,
        "previous_investigations": 0,
        "confirmed_sars": 0,
        "linked_exited_counterparties": 0
    }
}

# ==========================================
# 3. THE UPGRADED STRUCTURED CONTRACT
# ==========================================
class AutomatedTriageNarrative(BaseModel):
    """
    Defines the exact structural schema required by the front-end UI.
    Forces the text engine to populate structured slots rather than loose prose.
    """
    priority_justification: str = Field(description="Dynamic evaluation of why this alert sits in its tier.")
    salient_anomalies: List[str] = Field(description="List of specific flags discovered by worker agents.")
    investigator_playbook: List[str] = Field(description="Actionable next steps for the analyst review team.")

# ==========================================
# 4. WORKER RISK AGENTS (AGENTS 1-4)
# ==========================================
class BaseAgent(ABC):
    @abstractmethod
    def execute(self, alert_payload: Dict[str, Any]) -> float:
        pass

class RuleSeverityAgent(BaseAgent):
    def execute(self, alert_payload: Dict[str, Any]) -> float:
        logging.info("Analyzing rule exit historical telemetry...")
        time.sleep(0.05)
        rule_id = alert_payload.get("rule_id")
        rule_info = MOCK_RULES_DB.get(rule_id, {"historical_exit_rate": 0.20})
        return float(rule_info["historical_exit_rate"] * 100)

class HistoricalPerformanceAgent(BaseAgent):
    def execute(self, alert_payload: Dict[str, Any]) -> float:
        logging.info("Checking historical case management systems...")
        time.sleep(0.08)
        customer_id = alert_payload.get("customer_id")
        cust = MOCK_CUSTOMER_DB.get(customer_id, {})
        return float(min((cust.get("confirmed_sars", 0) * 50) + (cust.get("previous_investigations", 0) * 20), 100))

class CustomerRiskAgent(BaseAgent):
    def execute(self, alert_payload: Dict[str, Any]) -> float:
        logging.info("Calculating merchant entity baseline risk...")
        time.sleep(0.04)
        customer_id = alert_payload.get("customer_id")
        cust = MOCK_CUSTOMER_DB.get(customer_id, {})
        return float((cust.get("cash_intensity_score", 0) * 0.7) + (cust.get("jurisdiction_risk_score", 0) * 0.3))

class LinkAnalysisAgent(BaseAgent):
    def execute(self, alert_payload: Dict[str, Any]) -> float:
        logging.info("Running parallel transactional link mapping...")
        time.sleep(0.1)
        customer_id = alert_payload.get("customer_id")
        cust = MOCK_CUSTOMER_DB.get(customer_id, {})
        return float(min(cust.get("linked_exited_counterparties", 0) * 33.3, 100))

# ==========================================
# 5. DETERMINISTIC SCORING ENGINE (AGENT 5)
# ==========================================
class ScoringEngine:
    @staticmethod
    def calculate_risk(metrics: Dict[str, float], weights: Dict[str, float]) -> Dict[str, Any]:
        logging.info("Aggregating worker metrics inside math engine...")
        final_score = sum(metrics[key] * weights[key] for key in weights)
        
        if final_score >= 75:
            tier = "CRITICAL 🚨"
        elif final_score >= 50:
            tier = "HIGH ⚠️"
        else:
            tier = "MEDIUM/LOW"
            
        return {"final_score": round(final_score, 2), "priority_tier": tier}

# ==========================================
# 6. DYNAMIC ORCHESTRATOR LAYER (AGENT 6)
# ==========================================
class DynamicLLMNarrativeAgent:
    """
    Simulates the exact programmatic extraction layer of a Structured-Output LLM.
    Parses unstructured multi-agent telemetry and generates dynamic content.
    """
    def generate_summary(self, alert_payload: Dict[str, Any], telemetry: Dict[str, Any]) -> AutomatedTriageNarrative:
        logging.info("Executing Dynamic Narrative Synthesis Agent...")
        
        cust_id = alert_payload["customer_id"]
        rule_id = alert_payload["rule_id"]
        amt = alert_payload["transaction_amount"]
        
        scores = telemetry["agent_scores"]
        tier = telemetry["scoring_output"]["priority_tier"]
        final_score = telemetry["scoring_output"]["final_score"]
        
        # Pull raw context safely to alter phrasing dynamically based on customer state
        cust_profile = MOCK_CUSTOMER_DB.get(cust_id, {"name": "Unknown Entity", "industry": "General Corporate"})
        industry = cust_profile.get("industry")

        # --- DYNAMIC TEXT SYNTHESIS ENGINE ---
        # The code evaluates the data structure to build tailored content blocks on-the-fly
        anomalies = []
        playbook = ["Review full transaction history logs over the previous 90-day window."]
        
        if scores["link_analysis"] > 50:
            anomalies.append(f"Direct settlement vectors discovered interacting with {cust_profile.get('linked_exited_counterparties')} offboarded counterparties.")
            playbook.append("Map downstream counterparty accounts and file immediate network exposure flags.")
        
        if scores["customer_risk"] > 60:
            anomalies.append(f"Entity operates within a highly sensitive cash-intensive trade footprint: '{industry}'.")
            playbook.append("Request up-to-date corporate bank statements to reconcile physical vs digital asset turns.")
            
        if scores["historical_performance"] > 40:
            anomalies.append(f"Chronic compliance alerts found: {cust_profile.get('previous_investigations')} previous reviews with {cust_profile.get('confirmed_sars')} confirmed SAR filing(s).")
            playbook.append("Cross-reference historical SAR text narratives to find recurring transactional typologies.")
        else:
            anomalies.append("No material history of suspicious activity filings or persistent investigative escalation.")

        # Build dynamic contextual justification sentence structures
        primary_driver = max(scores, key=scores.get)
        justification = (
            f"Alert {alert_payload['alert_id']} triggered by client '{cust_profile['name']}' has been routed to the {tier} queue "
            f"with a score of {final_score}/100. This is dynamically driven by a peak indicator score within the '{primary_driver}' segment "
            f"coupled with the execution of core rule '{rule_id}' on a gross transaction velocity of £{amt:,.2f}."
        )

        # Map directly to the Pydantic type schema structure
        structured_output = AutomatedTriageNarrative(
            priority_justification=justification,
            salient_anomalies=anomalies,
            investigator_playbook=playbook
        )
        
        return structured_output

# ==========================================
# 7. CENTRAL PIPELINE RUNTIME CONTROL
# ==========================================
class AgenticTriageOrchestrator:
    def __init__(self):
        self.workers = {
            "rule_severity": RuleSeverityAgent(),
            "historical_performance": HistoricalPerformanceAgent(),
            "customer_risk": CustomerRiskAgent(),
            "link_analysis": LinkAnalysisAgent()
        }
        self.scoring_engine = ScoringEngine()
        self.narrative_engine = DynamicLLMNarrativeAgent()

    def process_pipeline(self, alert_payload: Dict[str, Any]) -> AutomatedTriageNarrative:
        logging.info(f"--- Launching Agentic Triage Pipeline: Alert {alert_payload['alert_id']} ---")
        agent_scores: Dict[str, float] = {}
        
        # Step 1: Execute worker agents 1-4 concurrently using standard thread pools
        with concurrent.futures.ThreadPoolExecutor(max_workers=4, thread_name_prefix="TriageWorker") as executor:
            future_to_agent = {
                executor.submit(agent.execute, alert_payload): name 
                for name, agent in self.workers.items()
            }
            
            for future in concurrent.futures.as_completed(future_to_agent):
                name = future_to_agent[future]
                agent_scores[name] = future.result()

        # Step 2: Compute deterministic score (Agent 5)
        scoring_results = self.scoring_engine.calculate_risk(agent_scores, SCORING_WEIGHTS)
        
        # Consolidate centralized environment payload
        telemetry_state = {
            "agent_scores": agent_scores,
            "scoring_output": scoring_results
        }
        
        # Step 3: Run the Dynamic Narrative Generation (Agent 6)
        structured_triage_package = self.narrative_engine.generate_summary(alert_payload, telemetry_state)
        
        return structured_triage_package

# ==========================================
# TEST RUNNERS
# ==========================================
if __name__ == "__main__":
    orchestrator = AgenticTriageOrchestrator()
    
    # CASE A: High Risk Profile (Taxi Merchant with complex network linkages)
    case_alpha = {
        "alert_id": "ALT-2026-X1",
        "customer_id": "CUST_9981",
        "rule_id": "R1002",
        "transaction_amount": 89450.00
    }
    
    # CASE B: Low Risk Profile (Consulting business with pristine history)
    case_beta = {
        "alert_id": "ALT-2026-Y2",
        "customer_id": "CUST_1234",
        "rule_id": "R1001",
        "transaction_amount": 2100.00
    }

    # Execute Batch Triage Run
    for current_case in [case_alpha, case_beta]:
        print("\n" + "="*80)
        result_package = orchestrator.process_pipeline(current_case)
        print("="*80)
        
        # Confirm that the output is an instantiation of the Pydantic template schema
        assert isinstance(result_package, AutomatedTriageNarrative)
        
        # Output clean JSON structured schemas for the Front-End view layer
        print(json.dumps(result_package.model_dump(), indent=2))
