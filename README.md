**AI Agentic Co-Refactoring Dashboard 🛠️🤖**

An intelligent, autonomous, multi-language code optimization pipeline powered by an agentic orchestration engine built on LangGraph and LangChain. This system ingests legacy, inefficient, or unoptimized code files (.py, .ipynb, .sql), passes them through safe runtime validation environments, intercepts security vulnerabilities, and exports production-grade code alongside granular markdown analytics reports.The repository features a fully integrated Streamlit interactive web interface for direct execution control, visual file navigation, and line-by-side comparative reviews.

**🏗️ Architectural Workflow**

The system moves away from basic "one-shot" AI prompts, instead utilising a stateful, cyclic multi-agent graph architecture. If code modifications break basic safety guardrails or fail functional runtimes, the graph routes diagnostic errors back to the code generation node for dynamic adjustment.

               +-------------------------------------------------------+

               |        [batch_processor.py / app.py Ingestion]         |
               +---------------------------+---------------------------+
                                           |
                                           v [Packs Code into AgentState Schema]
                                           |
+------------------------------------------v-------------------------------------------+

| [orchestrator.py Loop Graph]                                                         |
|                                                                                      |
|   +-----------------------+                                                          |
|   |   1. agent_coder.py   | <----------+ Routing Cycle Loop (Max 3 passes)           |
|   +-----------+-----------+            |                                             |
|               |                        |                                             |
|               v [Refactored Code]      |                                             |
|               |                        |                                             |
|   +-----------v-----------+            |                                             |
|   |  2. agent_tester.py   |            | [If Execution / Security Fails]             |
|   +-----------+-----------+            |                                             |
|               |                        |                                             |
|               v [Sandbox Outputs]      |                                             |
|               |                        |                                             |
|   +-----------v-----------+            |                                             |
|   | 3. agent_guardrail.py | -----------+                                             |
|   +-----------+-----------+                                                          |
|               |                                                                      |
|               v [All Safety/Runtime Approvals Pass]                                  |
|               |                                                                      |
|   +-----------v-----------+                                                          |
|   |  4. Diff Generator    |                                                          |
|   +-----------+-----------+                                                          |
|               |                                                                      |
+------------------------------------------|-------------------------------------------+
                                           |
                                           v [Returns Terminal Payload Variables]
                                           |
               +---------------------------v---------------------------+

               |      [batch_processor.py Writes Output Files]         |
               |                                                       |
               |  ├── optimized_code/optimized_utils.py (.sql / .py)   |
               |  └── optimized_code/report_utils.md (Analytics Card)  |
               +-------------------------------------------------------+

**Core Node Execution Roles**

**agent_coder.py (The Optimization Agent):** Rewrites logic patterns using structural Pydantic parameters. Implements Context-Length Shaving (discarding old histories to avoid token-budget bleed) and Prompt Decay Strategy on execution cycles greater than two to prioritize micro-patch updates.

**agent_tester.py (The Secure Sandbox Agent):** Writes untrusted source strings into a secure Docker container sandbox (python:3.11-slim) with isolated network capabilities (network_mode="none"), memory ceilings (128m), and absolute execution timeouts (5.0s) to abort infinite loops or hidden remote code executions (RCE).

**agent_guardrail.py (The Security Agent):** Conducts pre-execution keyword interceptions along with deep semantic validation to catch malicious input vectors (e.g., hardcoded parameters, raw shell injection signatures).

**Diff Generator Node:** Performs text-line evaluations using Python's core difflib library to isolate exact line mutations for report output formatting.

**Project File Structure**

Ensure your workspace directory is exactly arranged as below:

agentic_refactor/
│
├── legacy_code/                  # 📁 Create manually: Put input files here
│   ├── sample_script.py          # Legacy Python logic script samples
│   ├── analytical_note.ipynb     # Untransformed Jupyter data science notebooks
│   └── database_query.sql        # High-latency, unindexed raw database queries
│
├── optimized_code/               # 📁 Generated automatically: Outputs target results
│   ├── optimized_sample_script.py
│   ├── report_sample_script.md   # Visual diagnostics & color-coded diff report
│   ├── optimized_database_query.sql
│   └── report_database_query.md  # Custom query optimization matrix
│
├── app.py                        # Streamlit web user application dashboard interface
├── batch_processor.py            # Automated command-line folder process scanner
├── orchestrator.py               # Main compilation path for the LangGraph framework
├── agent_coder.py                # Module 1: Refactoring / Optimization Node
├── agent_tester.py               # Module 2: Secure Docker Isolation Sandbox Node
├── agent_guardrail.py            # Module 3: Pre/Post static security inspection engine
├── config.py                     # Centralized LLM configuration file (GPT-4o)
├── state.py                      # Strongly typed global schema memory dictionary
└── README.md                     # Project documentation mapping
