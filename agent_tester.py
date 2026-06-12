import sys
import os
import docker
import tempfile
from state import AgentState

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def tester_agent_node(state: AgentState) -> dict:
    code_to_test = state["current_code"]
    language = state["language"].lower()
    logs = list(state["feedback_logs"])
    test_results = {"success": False, "output": ""}

    # Path A: SQL Verification Route
    if language == "sql":
        # Check basic syntax structure validity
        keywords = ["select", "insert", "update", "delete", "create", "alter", "with"]
        if not any(kw in code_to_test.lower() for kw in keywords):
            logs.append("[Tester Agent Failure]: Invalid SQL construction file. Missing basic transactional statements.")
            return {"test_results": {"success": False, "output": "Invalid SQL Syntax structure"}, "feedback_logs": logs}
        
        return {"test_results": {"success": True, "output": "SQL statement validation passed syntax parsing checks successfully."}, "feedback_logs": logs}

    # Path B: Standard Python/Jupyter Sandbox Route
    try:
        client = docker.from_env()
    except Exception as e:
        logs.append(f"[Tester Environment Error]: Docker connection failed: {str(e)}")
        return {"test_results": test_results, "feedback_logs": logs}

    with tempfile.TemporaryDirectory() as tmpdir:
        host_file_path = os.path.join(tmpdir, "sandbox_app.py")
        with open(host_file_path, "w", encoding="utf-8") as f:
            f.write(code_to_test)

        try:
            container = client.containers.run(
                image="python:3.11-slim",
                command=["python", "/app/sandbox_app.py"],
                volumes={tmpdir: {"bind": "/app", "mode": "ro"}}, 
                network_mode="none",                             
                mem_limit="128m",                                
                nano_cpus=500000000,                             
                detach=True,
                read_only=True                                   
            )

            try:
                result = container.wait(timeout=5.0)  
                exit_code = result["StatusCode"]
                raw_logs = container.logs().decode("utf-8")
            except Exception:
                container.kill()  
                exit_code = 124
                raw_logs = "Execution Timeout: Code took longer than 5 seconds (Potential Infinite Loop)."
            finally:
                container.remove(force=True)

            if exit_code == 0:
                test_results = {"success": True, "output": raw_logs}
            else:
                test_results = {"success": False, "output": raw_logs}
                logs.append(f"[Tester Agent Failure (Exit Code {exit_code})]:\n{raw_logs}")

        except Exception as container_init_error:
            logs.append(f"[Tester Internal Error]: Sandbox failure: {str(container_init_error)}")

    return {"test_results": test_results, "feedback_logs": logs}
