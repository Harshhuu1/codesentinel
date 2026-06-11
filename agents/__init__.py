from typing import TypedDict, List, Optional

class CodeReviewState(TypedDict):
    # Input
    code: str
    language: str
    
    # Guardrail results
    pii_detected: bool
    injection_detected: bool
    
    # Agent outputs
    security_issues: Optional[str]
    performance_issues: Optional[str]
    style_issues: Optional[str]
    critic_output: Optional[str]
    
    # Metadata
    agent_path: List[str]
    total_issues: int
    
    # Final output
    final_report: Optional[str]
    error: Optional[str]