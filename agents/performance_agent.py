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

PERFORMANCE_PROMPT = """You are an expert code performance reviewer. Analyze the given code for:
- Time complexity issues (nested loops, redundant iterations)
- Space complexity issues (unnecessary data structures, memory leaks)
- Database query optimization (N+1 queries, missing indexes)
- Caching opportunities
- Algorithmic improvements

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
FINDINGS: No performance issues detected.
"""

def performance_node(state: CodeReviewState) -> CodeReviewState:
    start = time.time()

    try:
        messages = [
            SystemMessage(content=PERFORMANCE_PROMPT),
            HumanMessage(content=f"Language: {state['language']}\n\nCode:\n{state['code']}")
        ]

        response = llm.invoke(messages)
        state["performance_issues"] = response.content.strip()
        state["agent_path"].append("performance")

    except Exception as e:
        state["performance_issues"] = f"Performance agent error: {str(e)}"
        state["agent_path"].append("performance_failed")

    return state