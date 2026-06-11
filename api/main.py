from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.graph import review_graph
from agents import CodeReviewState
from observability.logger import AgentLogger
import uvicorn
from config import API_HOST, API_PORT

app = FastAPI(
    title="CodeSentinel API",
    description="Multi-agent code review system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class ReviewRequest(BaseModel):
    code: str
    language: str = ""

class ReviewResponse(BaseModel):
    security_issues: str
    performance_issues: str
    style_issues: str
    critic_output: str
    agent_path: list
    total_issues: int
    language: str

@app.get("/")
def root():
    return {"status": "CodeSentinel is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/review", response_model=ReviewResponse)
def review_code(request: ReviewRequest):
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")

    if len(request.code) > 10000:
        raise HTTPException(status_code=400, detail="Code too long, max 10000 characters")

    logger = AgentLogger()

    try:
        logger.start_session(request.code)

        # run input guardrail first
        from guardrails.input_guard import run_input_guard
        input_guard_result = run_input_guard(request.code)
        
        logger.log_guardrail("input_guard", input_guard_result["blocked"])
        logger.log_guardrail("pii_detected", input_guard_result["pii"]["detected"])

        if input_guard_result["blocked"]:
            raise HTTPException(
                status_code=400,
                detail=f"Input blocked: {input_guard_result['message']}"
            )

        initial_state: CodeReviewState = {
            "code": request.code,
            "language": request.language,
            "pii_detected": input_guard_result["pii"]["detected"],
            "injection_detected": input_guard_result["injection"]["detected"],
            "security_issues": None,
            "performance_issues": None,
            "style_issues": None,
            "critic_output": None,
            "agent_path": [],
            "total_issues": 0,
            "final_report": None,
            "error": None
        }

        result = review_graph.invoke(initial_state)

        # run output guardrail on critic output
        from guardrails.output_guard import run_output_guard
        output_guard_result = run_output_guard(
            result["critic_output"] or "",
            "critic"
        )
        logger.log_guardrail("output_flagged", output_guard_result["flagged"])

        logger.log_final(
            agent_path=result["agent_path"],
            total_issues=result["total_issues"]
        )

        return ReviewResponse(
            security_issues=result["security_issues"] or "",
            performance_issues=result["performance_issues"] or "",
            style_issues=result["style_issues"] or "",
            critic_output=result["critic_output"] or "",
            agent_path=result["agent_path"],
            total_issues=result["total_issues"],
            language=result["language"]
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        logger.end_session()

if __name__ == "__main__":
    uvicorn.run("api.main:app", host=API_HOST, port=API_PORT, reload=True)