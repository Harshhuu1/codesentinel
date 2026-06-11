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

STYLE_PROMPT = """You are an expert code style and readability reviewer. Analyze the given code for:
- Naming conventions (variables, functions, classes)
- Code documentation (missing docstrings, comments)
- Function length and single responsibility principle
- Code duplication (DRY violations)
- Error handling completeness
- Code organization and structure

Format your response EXACTLY like this:
ISSUES_COUNT: <number>
SEVERITY: <LOW|MEDIUM|HIGH>
FINDINGS:
1. <issue title>
   - Location: <where in code>
   - Problem: <what is wrong>
   - Fix: <how to fix it>

If no issues found, respond with:
ISSUES_COUNT: 0
SEVERITY: LOW
FINDINGS: No style issues detected.
"""

def style_node(state: CodeReviewState) -> CodeReviewState:
    start = time.time()

    try:
        messages = [
            SystemMessage(content=STYLE_PROMPT),
            HumanMessage(content=f"Language: {state['language']}\n\nCode:\n{state['code']}")
        ]

        response = llm.invoke(messages)
        state["style_issues"] = response.content.strip()
        state["agent_path"].append("style")

    except Exception as e:
        state["style_issues"] = f"Style agent error: {str(e)}"
        state["agent_path"].append("style_failed")

    return state