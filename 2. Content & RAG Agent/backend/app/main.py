"""
main.py — Content Reducer FastAPI 서버 진입점 (M2)

Orchestrator(1번), 백엔드(3번), 프론트엔드(4번)가 호출할 수 있는 REST API 엔드포인트를 제공한다.

실행 방법:
  uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# 환경 변수 로드
load_dotenv()

from backend.app.agents.content_reducer.contracts import (
    ReadingSessionState,
    ContentReducerRequest,
    ContentReducerResponse,
    QuizGenerationRequest,
    QuizDict
)
from backend.app.agents.content_reducer.agent import run_content_reducer
from backend.app.agents.content_reducer.quiz_generator import generate_quiz

app = FastAPI(
    title="AI Literacy Care - Content Reducer API",
    description="가독성 분석, 의미 청킹, LLM 기반 쉬운 문장 재구성 및 RAG 용어풀이를 담당하는 2번 에이전트 서비스",
    version="1.0.0"
)

# CORS 설정 (프론트엔드 연동 지원)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic 스키마 정의 (FastAPI 자동 문서화 및 타입 검증용)
# ---------------------------------------------------------------------------

class ContentReducerRequestModel(BaseModel):
    session_id: str = Field(..., description="세션 식별자")
    raw_text: str = Field(..., description="분석할 원문 텍스트")
    user_literacy_level: int = Field(3, ge=1, le=5, description="사용자 문해력 수준 (1~5)")
    target_domain: str | None = Field("일반", description="도메인 영역")
    profile: dict | None = Field(default_factory=dict, description="사용자 세부 프로필")


class QuizGenerationRequestModel(BaseModel):
    session_id: str = Field(..., description="세션 식별자")
    chunk_id: str = Field(..., description="문제를 생성할 청크 ID")
    context: str = Field(..., description="청크의 재구성된 텍스트")
    user_literacy_level: int | None = Field(3, ge=1, le=5, description="사용자 문해력 수준")


# ---------------------------------------------------------------------------
# 엔드포인트 구현
# ---------------------------------------------------------------------------

@app.get("/health")
def health_check():
    """서버 헬스 체크."""
    return {
        "status": "healthy",
        "agent": "Content & RAG Reducer Agent (Role 2)",
        "mode": os.getenv("CONTENT_REDUCER_MODE", "real"),
        "rag_mode": os.getenv("RAG_MODE", "memory")
    }


@app.post("/api/content-reducer/reduce", response_model=dict)
def reduce_content(req: ContentReducerRequestModel):
    """
    원문을 입력받아 가독성 점수, 의미 단위 청킹, 쉬운 문장 재구성 및 RAG 용어풀이를 일괄 수행한다.
    Orchestrator 혹은 프론트엔드에서 세션 로드 시 호출.
    """
    # ReadingSessionState 스키마로 가공하여 에이전트 진입점 호출
    state: ReadingSessionState = {
        "session_id": req.session_id,
        "user_id": req.profile.get("user_id", "default_user") if req.profile else "default_user",
        "document_id": req.profile.get("document_id", "default_doc") if req.profile else "default_doc",
        "raw_text": req.raw_text,
        "profile": {
            "user_literacy_level": req.user_literacy_level,
            "target_domain": req.target_domain,
            **(req.profile or {})
        },
        "trace": [],
        "errors": []
    }
    
    try:
        updated_state = run_content_reducer(state)
        
        # API Response 규격에 맞춰 추출
        return {
            "session_id": updated_state.get("session_id"),
            "readability_score": updated_state.get("readability_score", 50.0),
            "difficulty_score": updated_state.get("difficulty_score", 50.0),
            "chunks": updated_state.get("chunks", []),
            "simplified_text": updated_state.get("simplified_text", ""),
            "terms": updated_state.get("terms", []),
            "trace": updated_state.get("trace", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content reduction failed: {str(e)}")


@app.post("/api/content-reducer/quiz", response_model=dict)
def get_quiz(req: QuizGenerationRequestModel):
    """
    특정 청크 텍스트에 대한 맞춤형 독해력 확인 퀴즈를 생성한다.
    개입 트리거(3번 에이전트 신호) 수신 후 Orchestrator에서 호출.
    """
    try:
        quiz = generate_quiz(req.chunk_id, req.context)
        return quiz
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {str(e)}")
