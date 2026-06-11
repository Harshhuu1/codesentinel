import re

# patterns that suggest hallucination or bad output
HALLUCINATION_PATTERNS = [
    r"as an ai language model",
    r"i cannot (access|browse|search)",
    r"i don't have (access|the ability)",
    r"as of my (last|knowledge) (update|cutoff)",
    r"i'm not able to",
]

# valid severity levels
VALID_SEVERITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

def check_hallucination(output: str) -> dict:
    output_lower = output.lower()
    triggered = []

    for pattern in HALLUCINATION_PATTERNS:
        if re.search(pattern, output_lower):
            triggered.append(pattern)

    return {
        "detected": len(triggered) > 0,
        "patterns_matched": triggered,
        "count": len(triggered)
    }

def check_format(output: str) -> dict:
    has_issues_count = bool(re.search(r"ISSUES_COUNT:\s*\d+", output))
    has_severity = any(s in output for s in VALID_SEVERITIES)
    has_findings = "FINDINGS:" in output

    issues = []
    if not has_issues_count:
        issues.append("Missing ISSUES_COUNT field")
    if not has_severity:
        issues.append("Missing SEVERITY field")
    if not has_findings:
        issues.append("Missing FINDINGS field")

    return {
        "valid": len(issues) == 0,
        "issues": issues
    }

def extract_severity(output: str) -> str:
    for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        if severity in output:
            return severity
    return "UNKNOWN"

def run_output_guard(output: str, agent_name: str) -> dict:
    hallucination = check_hallucination(output)
    format_check = check_format(output)
    severity = extract_severity(output)

    flagged = hallucination["detected"] or not format_check["valid"]

    return {
        "agent": agent_name,
        "flagged": flagged,
        "severity": severity,
        "hallucination": hallucination,
        "format": format_check,
        "message": "Output flagged for review" if flagged else "OK"
    }