from langgraph.graph import StateGraph, END
from agents import CodeReviewState
from agents.supervisor import supervisor_node
from agents.security_agent import security_node
from agents.performance_agent import performance_node
from agents.style_agent import style_node
from agents.critic_agent import critic_node

def build_graph():
    graph = StateGraph(CodeReviewState)

    # add all nodes
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("security", security_node)
    graph.add_node("performance", performance_node)
    graph.add_node("style", style_node)
    graph.add_node("critic", critic_node)

    # entry point
    graph.set_entry_point("supervisor")

    # sequential execution
    graph.add_edge("supervisor", "security")
    graph.add_edge("security", "performance")
    graph.add_edge("performance", "style")
    graph.add_edge("style", "critic")
    graph.add_edge("critic", END)

    return graph.compile()


review_graph = build_graph()