from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from config import OPENAI_API_KEY, OPENAI_MODEL
from agents import CodeReviewState
import time
import re

llm = ChatOpenAI(
    model=OPENAI_MODEL,
    api_key=OPENAI_API_KEY,
    temperature=0
)

CRITIC_PROMPT = """You are a senior code review critic. You receive outputs from three specialist agents:
1. Security Agent
2. Performance Agent  
3. Style Agent

Your job is to:
- Identify any contradictions between agents
- Remove duplicate findings across agents
- Validate that findings are real and not hallucinated
- Assign a final overall severity score
- Produce a clean consolidated report

Format your response EXACTLY like this:
OVERALL_SEVERITY: <LOW|MEDIUM|HIGH|CRITICAL>
TOTAL_ISSUES: <number>
CONTRADICTIONS: <any contradictions found, or "None">
CONSOLIDATED_REPORT:
<A clean, well structured summary of all valid findings grouped by category>

RECOMMENDATION:
<Overall recommendation for the code - approve, approve with minor fixes, or reject>
"""

def parse_total_issues(critic_output: str) -> int:
    match = re.search(r"TOTAL_ISSUES:\s*(\d+)", critic_output)
    if match:
        return int(match.group(1))
    return 0

def critic_node(state: CodeReviewState) -> CodeReviewState:
    start = time.time()

    try:
        combined_input = f"""
SECURITY AGENT OUTPUT:
{state.get('security_issues', 'No output')}

PERFORMANCE AGENT OUTPUT:
{state.get('performance_issues', 'No output')}

STYLE AGENT OUTPUT:
{state.get('style_issues', 'No output')}

Original Code Language: {state.get('language', 'unknown')}
"""

        messages = [
            SystemMessage(content=CRITIC_PROMPT),
            HumanMessage(content=combined_input)
        ]

        response = llm.invoke(messages)
        critic_output = response.content.strip()

        state["critic_output"] = critic_output
        state["total_issues"] = parse_total_issues(critic_output)
        state["agent_path"].append("critic")

    except Exception as e:
        state["critic_output"] = f"Critic agent error: {str(e)}"
        state["total_issues"] = 0
        state["agent_path"].append("critic_failed")

    return state