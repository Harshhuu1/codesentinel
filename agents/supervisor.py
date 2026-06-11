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

SUPERVISOR_PROMPT = """You are a code review supervisor. Analyze the given code and decide which specialist agents to invoke.

Available agents:
- security: checks for vulnerabilities, injections, insecure practices
- performance: checks for complexity, bottlenecks, optimization opportunities  
- style: checks for readability, naming conventions, documentation

Respond ONLY with a JSON object like this:
{
    "agents": ["security", "performance", "style"],
    "language": "python",
    "reasoning": "brief reason"
}

Always include all 3 agents unless the code is trivially simple.
"""

def supervisor_node(state: CodeReviewState) -> CodeReviewState:
    start = time.time()
    
    try:
        messages = [
            SystemMessage(content=SUPERVISOR_PROMPT),
            HumanMessage(content=f"Analyze this code:\n\n{state['code']}")
        ]
        
        response = llm.invoke(messages)
        content = response.content.strip()
        
        # parse JSON response
        import json
        # strip markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        parsed = json.loads(content)
        
        state["language"] = parsed.get("language", "unknown")
        state["agent_path"] = ["supervisor"]
        state["error"] = None
        
    except Exception as e:
        state["agent_path"] = ["supervisor"]
        state["language"] = "unknown"
        state["error"] = str(e)
    
    return state