import traceback

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from agent import chat
from logger import get_logger, setup_logging
from models import ChatRequest, ChatResponse

setup_logging()
log = get_logger("main")

app = FastAPI(title="CarDekho AI Advisor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log.error("Unhandled exception on %s\n%s", request.url, traceback.format_exc())
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    log.info("session=%s | user: %s", req.session_id[:8], req.message)
    try:
        result = chat(req.session_id, req.message)
        log.info("session=%s | agent type=%s | msg=%s", req.session_id[:8], result.get("type"), result.get("message", "")[:120])
        return ChatResponse(
            type=result.get("type", "message"),
            message=result.get("message", ""),
            cars=result.get("cars"),
        )
    except Exception as exc:
        log.error("session=%s | chat() failed\n%s", req.session_id[:8], traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/health")
def health():
    return {"status": "ok"}
