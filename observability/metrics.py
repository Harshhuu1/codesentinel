import mlflow
import time
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class SessionMetrics:
    session_id: str
    start_time: float = field(default_factory=time.time)
    agent_latencies: dict = field(default_factory=dict)
    agent_tokens: dict = field(default_factory=dict)
    guardrail_triggers: dict = field(default_factory=dict)
    total_issues: int = 0
    agent_path: List[str] = field(default_factory=list)
    language: str = "unknown"
    blocked: bool = False

    def total_latency(self) -> float:
        return time.time() - self.start_time

    def total_tokens(self) -> int:
        return sum(self.agent_tokens.values())

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "total_latency": round(self.total_latency(), 2),
            "total_tokens": self.total_tokens(),
            "total_issues": self.total_issues,
            "agent_path": " -> ".join(self.agent_path),
            "language": self.language,
            "blocked": self.blocked,
            "guardrail_triggers": self.guardrail_triggers,
            "agent_latencies": self.agent_latencies,
        }


def log_session_to_mlflow(metrics: SessionMetrics):
    with mlflow.start_run():
        mlflow.log_param("session_id", metrics.session_id)
        mlflow.log_param("language", metrics.language)
        mlflow.log_param("agent_path", " -> ".join(metrics.agent_path))
        mlflow.log_metric("total_latency", metrics.total_latency())
        mlflow.log_metric("total_tokens", metrics.total_tokens())
        mlflow.log_metric("total_issues", metrics.total_issues)
        mlflow.log_metric("blocked", int(metrics.blocked))

        for agent, latency in metrics.agent_latencies.items():
            mlflow.log_metric(f"{agent}_latency", latency)

        for guard, triggered in metrics.guardrail_triggers.items():
            mlflow.log_metric(f"{guard}_triggered", int(triggered))