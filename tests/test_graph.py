from agents.graph import review_graph
from agents import CodeReviewState

test_code = """
import sqlite3

def get_user(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchone()
"""

initial_state: CodeReviewState = {
    "code": test_code,
    "language": "",
    "pii_detected": False,
    "injection_detected": False,
    "security_issues": None,
    "performance_issues": None,
    "style_issues": None,
    "critic_output": None,
    "agent_path": [],
    "total_issues": 0,
    "final_report": None,
    "error": None
}

if __name__ == "__main__":
    print("Running CodeSentinel graph...")
    result = review_graph.invoke(initial_state)
    print("\n--- AGENT PATH ---")
    print(" -> ".join(result["agent_path"]))
    print("\n--- SECURITY ---")
    print(result["security_issues"])
    print("\n--- PERFORMANCE ---")
    print(result["performance_issues"])
    print("\n--- STYLE ---")
    print(result["style_issues"])
    print("\n--- CRITIC FINAL REPORT ---")
    print(result["critic_output"])
    print("\n--- TOTAL ISSUES ---")
    print(result["total_issues"])