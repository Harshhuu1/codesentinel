# CodeSentinel

A production-grade multi-agent code review system built with LangGraph. Submits code through a pipeline of 5 specialized AI agents — each focused on a different dimension of code quality — with a final Critic agent that cross-validates and consolidates all findings before returning a structured report.

Live demo: https://codesentinel-iyntwu75weecmcb4fezpoe.streamlit.app  
API: https://codesentinel-wkn5.onrender.com

---

## How it works
User submits code

|

Input Guardrail

(PII detection + prompt injection check)

|

Supervisor Agent

(detects language, initializes pipeline)

|

┌────────────────────────────────────┐

│  Security Agent                    │

│  SQL injection, XSS, hardcoded     │

│  secrets, path traversal, CVEs     │

├────────────────────────────────────┤

│  Performance Agent                 │

│  Time/space complexity, N+1        │

│  queries, caching opportunities    │

├────────────────────────────────────┤

│  Style Agent                       │

│  Naming, documentation, DRY,       │

│  error handling, SRP               │

└────────────────────────────────────┘

|

Critic Agent

(removes duplicates, flags contradictions,

assigns overall severity, final report)

|

Output Guardrail

(hallucination check, format validation)

|

Structured Review Report

(logged to MLflow)

Each agent operates on a shared typed state object (`CodeReviewState`) and writes only to its own fields. The Critic agent receives all three specialist outputs simultaneously and produces a consolidated report with an overall severity rating and recommendation.

---

## Architecture

codesentinel/

├── agents/

│   ├── init.py          # CodeReviewState TypedDict

│   ├── graph.py             # LangGraph StateGraph pipeline

│   ├── supervisor.py        # language detection, pipeline init

│   ├── security_agent.py    # vulnerability detection

│   ├── performance_agent.py # complexity and optimization

│   ├── style_agent.py       # readability and conventions

│   └── critic_agent.py      # cross-validation and consolidation

├── guardrails/

│   ├── input_guard.py       # Presidio PII + injection detection

│   └── output_guard.py      # hallucination scoring, format check

├── observability/

│   ├── logger.py            # MLflow session logging

│   └── metrics.py           # per-agent latency, token tracking

├── api/

│   └── main.py              # FastAPI endpoints

├── ui/

│   └── app.py               # Streamlit frontend

├── tests/

│   ├── test_graph.py        # end-to-end pipeline test

│   └── eval_harness.py      # automated eval across 10 vuln categories

└── config/

└── settings.py          # centralized config, env vars

---

## Stack

| Layer | Technology |
|---|---|
| Agent orchestration | LangGraph |
| LLM | GPT-4o-mini / Groq Llama-3.1-70B |
| PII detection | Microsoft Presidio |
| Experiment tracking | MLflow |
| Backend API | FastAPI |
| Frontend | Streamlit |
| Deployment | Render (API), Streamlit Cloud (UI) |

---

## Guardrails

**Input guardrail** runs before any LLM call:
- Presidio analyzer scans for PII entities (emails, phone numbers, API keys, credit cards)
- Regex classifier detects 10 prompt injection patterns
- Blocked requests return HTTP 400 before reaching the agent pipeline

**Output guardrail** runs after the Critic agent:
- Checks for hallucination markers (AI refusal phrases, off-topic responses)
- Validates structured output format (ISSUES_COUNT, SEVERITY, FINDINGS fields)
- Flags malformed outputs for review

---

## Eval

Automated evaluation harness across 10 vulnerability categories:

| Category | Example Pattern |
|---|---|
| SQL Injection | String concatenation in DB queries |
| Hardcoded Secrets | API keys, AWS credentials in source |
| Path Traversal | User input appended to file paths |
| Command Injection | os.system with unsanitized input |
| Insecure Deserialization | pickle.loads on untrusted data |
| XSS | innerHTML assignment from user input |
| Weak Cryptography | MD5 password hashing |
| Missing Auth | Destructive operations without auth checks |
| Sensitive Data Exposure | Passwords logged to stdout |
| Integer Overflow | Unchecked buffer size calculations |

Baseline detection rate measured via `tests/eval_harness.py`

---

## Running locally

```bash
git clone https://github.com/Harshhuu1/codesentinel.git
cd codesentinel
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

Create a `.env` file:
OPENAI_API_KEY=your_key_here

HF_TOKEN=your_hf_token_here

MLFLOW_ALLOW_FILE_STORE=true

Start the API:
```bash
python -m api.main
```

Start the UI (separate terminal):
```bash
python -m streamlit run ui/app.py
```

Run the eval harness:
```bash
python -m tests.eval_harness
```

---

## Roadmap

- [ ] Swap Security Agent with fine-tuned Phi-3-mini (DPO on CyberNative security dataset)
- [ ] Measure detection rate delta vs GPT-4o-mini baseline
- [ ] GitHub Actions CI/CD pipeline
- [ ] Support for file upload (.py, .js, .java)
- [ ] Per-session MLflow dashboard in UI