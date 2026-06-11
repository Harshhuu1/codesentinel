import os
from dotenv import load_dotenv

load_dotenv()

# LLM
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"

# HuggingFace
HF_TOKEN = os.getenv("HF_TOKEN")
SECURITY_MODEL_ID = os.getenv("SECURITY_MODEL_ID", "Harshhuu1/phi3-security-agent")

# MLflow
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "mlruns")
MLFLOW_EXPERIMENT_NAME = "codesentinel"

# Guardrails
PROMPT_INJECTION_THRESHOLD = 0.85
PII_ENTITIES = ["PHONE_NUMBER", "EMAIL_ADDRESS", "CRYPTO", "CREDIT_CARD", "API_KEY"]

# Agent config
MAX_RETRIES = 3
AGENT_TIMEOUT = 30

# FastAPI
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))