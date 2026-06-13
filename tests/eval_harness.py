import requests
import json
import time

API_URL = "http://localhost:8000"

# 10 test cases with known vulnerabilities
TEST_CASES = [
    {
        "id": 1,
        "language": "python",
        "expected_issues": ["sql injection"],
        "code": """
def get_user(username):
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    return db.execute(query)
"""
    },
    {
        "id": 2,
        "language": "python",
        "expected_issues": ["hardcoded secret"],
        "code": """
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
def connect():
    return boto3.client('s3', aws_secret_access_key=AWS_SECRET_KEY)
"""
    },
    {
        "id": 3,
        "language": "python",
        "expected_issues": ["path traversal"],
        "code": """
def read_file(filename):
    with open("/var/data/" + filename) as f:
        return f.read()
"""
    },
    {
        "id": 4,
        "language": "python",
        "expected_issues": ["command injection"],
        "code": """
import os
def ping_host(host):
    os.system("ping -c 1 " + host)
"""
    },
    {
        "id": 5,
        "language": "python",
        "expected_issues": ["insecure deserialization"],
        "code": """
import pickle
def load_data(data):
    return pickle.loads(data)
"""
    },
    {
        "id": 6,
        "language": "javascript",
        "expected_issues": ["xss"],
        "code": """
function renderUser(username) {
    document.getElementById('user').innerHTML = username;
}
"""
    },
    {
        "id": 7,
        "language": "python",
        "expected_issues": ["weak cryptography"],
        "code": """
import hashlib
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()
"""
    },
    {
        "id": 8,
        "language": "python",
        "expected_issues": ["no authentication"],
        "code": """
def delete_user(user_id):
    db.execute(f"DELETE FROM users WHERE id={user_id}")
    return "deleted"
"""
    },
    {
        "id": 9,
        "language": "python",
        "expected_issues": ["sensitive data exposure"],
        "code": """
def login(username, password):
    print(f"Login attempt: {username} / {password}")
    return authenticate(username, password)
"""
    },
    {
        "id": 10,
        "language": "python",
        "expected_issues": ["integer overflow"],
        "code": """
def calculate_buffer(size):
    buffer_size = size * 1024 * 1024
    return bytearray(buffer_size)
"""
    },
]

def evaluate():
    results = []
    detected = 0
    total = len(TEST_CASES)

    print(f"Running eval on {total} test cases...\n")

    keyword_map = {
        "sql injection": ["sql injection", "sql", "injection", "query"],
        "hardcoded secret": ["hardcoded", "secret", "api key", "credential"],
        "path traversal": ["path traversal", "traversal", "directory"],
        "command injection": ["command injection", "os.system", "shell injection"],
        "insecure deserialization": ["deserialization", "pickle", "deserializ"],
        "xss": ["xss", "cross-site", "innerhtml", "script injection"],
        "weak cryptography": ["md5", "weak", "cryptograph", "hash"],
        "no authentication": ["authentication", "authorization", "access control"],
        "sensitive data exposure": ["sensitive", "password", "logging", "exposure"],
        "integer overflow": ["overflow", "integer", "buffer size"],
    }

    for case in TEST_CASES:
        start = time.time()
        try:
            response = requests.post(
                f"{API_URL}/review",
                json={"code": case["code"], "language": case["language"]},
                timeout=60
            )
            latency = time.time() - start

            if response.status_code == 200:
                data = response.json()
                security_output = data["security_issues"].lower()
                critic_output = data["critic_output"].lower()

                expected = case["expected_issues"][0].lower()
                keywords = keyword_map.get(expected, [expected])
                found = any(kw in security_output or kw in critic_output for kw in keywords)

                if found:
                    detected += 1

                results.append({
                    "id": case["id"],
                    "expected": case["expected_issues"][0],
                    "detected": found,
                    "total_issues": data["total_issues"],
                    "latency": round(latency, 2)
                })

                status = "PASS" if found else "FAIL"
                print(f"[{status}] Case {case['id']} - {case['expected_issues'][0]} | issues: {data['total_issues']} | {round(latency,2)}s")

            else:
                print(f"[ERROR] Case {case['id']} - API returned {response.status_code}")

        except Exception as e:
            print(f"[ERROR] Case {case['id']} - {str(e)}")

    precision = detected / total * 100
    avg_latency = sum(r["latency"] for r in results) / len(results)

    print(f"\n{'='*50}")
    print(f"EVAL RESULTS")
    print(f"{'='*50}")
    print(f"Detection Rate : {detected}/{total} ({precision:.1f}%)")
    print(f"Avg Latency    : {avg_latency:.2f}s per review")
    print(f"{'='*50}")

    return {
        "detection_rate": precision,
        "detected": detected,
        "total": total,
        "avg_latency": avg_latency,
        "results": results
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "debug":
        # debug mode - print raw output for each case
        for case in TEST_CASES:
            print(f"\n{'='*40}")
            print(f"Case {case['id']} - {case['expected_issues'][0]}")
            print(f"{'='*40}")
            response = requests.post(
                f"{API_URL}/review",
                json={"code": case["code"], "language": case["language"]},
                timeout=60
            )
            if response.status_code == 200:
                data = response.json()
                print(f"SECURITY OUTPUT:\n{data['security_issues'][:300]}")
                print(f"\nTOTAL ISSUES: {data['total_issues']}")
    else:
        evaluate()