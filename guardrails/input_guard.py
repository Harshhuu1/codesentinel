from presidio_analyzer import AnalyzerEngine
from config import PII_ENTITIES
import re

analyzer = AnalyzerEngine()

# common prompt injection patterns
INJECTION_PATTERNS = [
    r"ignore (all )?previous instructions",
    r"disregard (all )?previous",
    r"forget (all )?previous",
    r"you are now",
    r"act as (a|an)",
    r"pretend (you are|to be)",
    r"your new instructions",
    r"system prompt",
    r"bypass",
    r"jailbreak",
]

def detect_pii(code: str) -> dict:
    results = analyzer.analyze(text=code, language="en", entities=PII_ENTITIES)
    
    findings = []
    for result in results:
        findings.append({
            "entity_type": result.entity_type,
            "start": result.start,
            "end": result.end,
            "score": round(result.score, 2)
        })
    
    return {
        "detected": len(findings) > 0,
        "findings": findings,
        "count": len(findings)
    }

def detect_injection(text: str) -> dict:
    text_lower = text.lower()
    triggered = []
    
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text_lower):
            triggered.append(pattern)
    
    return {
        "detected": len(triggered) > 0,
        "patterns_matched": triggered,
        "count": len(triggered)
    }

def run_input_guard(code: str) -> dict:
    pii_result = detect_pii(code)
    injection_result = detect_injection(code)
    
    blocked = injection_result["detected"]  # block on injection, warn on PII
    
    return {
        "blocked": blocked,
        "pii": pii_result,
        "injection": injection_result,
        "message": "Prompt injection detected" if blocked else "OK"
    }