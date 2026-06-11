import mlflow
import time
from datetime import datetime
from config import MLFLOW_TRACKING_URI, MLFLOW_EXPERIMENT_NAME

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

class AgentLogger:
    def __init__(self):
        self.run = None

    def start_session(self, code_snippet: str):
        self.run = mlflow.start_run()
        mlflow.log_param("timestamp", datetime.now().isoformat())
        mlflow.log_param("code_length", len(code_snippet))
        self.session_start = time.time()

    def log_agent(self, agent_name: str, latency: float, tokens_used: int, output_length: int):
        mlflow.log_metric(f"{agent_name}_latency", latency)
        mlflow.log_metric(f"{agent_name}_tokens", tokens_used)
        mlflow.log_metric(f"{agent_name}_output_length", output_length)

    def log_guardrail(self, guard_name: str, triggered: bool):
        mlflow.log_metric(f"{guard_name}_triggered", int(triggered))

    def log_final(self, agent_path: list, total_issues: int):
        mlflow.log_metric("total_latency", time.time() - self.session_start)
        mlflow.log_param("agent_path", " -> ".join(agent_path))
        mlflow.log_metric("total_issues_found", total_issues)

    def end_session(self):
        if self.run:
            mlflow.end_run()

logger = AgentLogger()