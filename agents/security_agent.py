from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from config import OPENAI_API_KEY, OPENAI_MODEL
from agents import CodeReviewState
import time

llm = ChatOpenAI(
    model=OPENAI_MODEL,
    api_key=OPENAI_API_KEY,
    temperature=0
)

SECURITY_PROMPT = """You are an expert code security reviewer. Analyze the given code for:
- SQL injection vulnerabilities
- XSS vulnerabilities
- Hardcoded secrets, API keys, passwords
- Insecure cryptography usage
- Path traversal vulnerabilities
- Insecure deserialization
- Missing authentication/authorization checks
- Sensitive data exposure
- Known CVE patterns

Format your response EXACTLY like this:
ISSUES_COUNT: <number>
SEVERITY: <LOW|MEDIUM|HIGH|CRITICAL>
FINDINGS:
1. <issue title>
   - Location: <where in code>
   - Problem: <what is wrong>
   - CVE: <CVE number if applicable, else N/A>
   - Fix: <how to fix it>

If no issues found, respond with:
ISSUES_COUNT: 0
SEVERITY: LOW
FINDINGS: No security issues detected.
"""

def security_node(state: CodeReviewState) -> CodeReviewState:
    start = time.time()

    try:
        messages = [
            SystemMessage(content=SECURITY_PROMPT),
            HumanMessage(content=f"Language: {state['language']}\n\nCode:\n{state['code']}")
        ]

        response = llm.invoke(messages)
        state["security_issues"] = response.content.strip()
        state["agent_path"].append("security")

    except Exception as e:
        state["security_issues"] = f"Security agent error: {str(e)}"
        state["agent_path"].append("security_failed")

    return state