"""FastAPI entrypoint for the AI Literacy Care Agent backend."""

from __future__ import annotations

from fastapi import FastAPI

from backend.app.api.reading_session import router as reading_session_router

app = FastAPI(title="AI Literacy Care Agent", version="0.1.0")
app.include_router(reading_session_router, prefix="/api")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
