"""
restructurer.py — LLM 기반 문단 요약 모듈 (M1)

사용자의 리터러시 프로필과 텍스트 난이도에 따라
Claude/Gemini API를 호출하여 1문장 요약으로 변환한다.

동작 모드:
  CONTENT_REDUCER_MODE=real (기본):
    → ANTHROPIC_API_KEY가 있으면 실제 Claude API 호출
    → API 키 없으면 DEMO 모드로 자동 전환

  CONTENT_REDUCER_MODE=stub:
    → 원문 앞에 [레벨 수준] 접두사 추가 (API 없이 빠른 테스트용)

  DEMO_MODE=true:
    → API 없이 데모용 텍스트 반환

실패 시 Fallback: 원문 텍스트를 그대로 반환 (절대 예외 전파 안 함)
"""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

from backend.app.agents.content_reducer.contracts import ChunkDict
from backend.app.agents.content_reducer.prompts import (
    SUMMARY_SYSTEM_PROMPT,
    build_summary_prompt,
)
from backend.app.agents.content_reducer.router import get_routing_reason, select_model

# ---------------------------------------------------------------------------
# 환경 설정
# ---------------------------------------------------------------------------
# 실행 시점에 환경 변수를 동적으로 읽도록 변경함


# ---------------------------------------------------------------------------
# 고품질 데모 폴백 데이터 로드
# ---------------------------------------------------------------------------

def _load_fallback_data() -> dict:
    try:
        root = Path(__file__).resolve().parents[4]
        path = root / "data" / "demo_fallback_data.json"
        if path.exists():
            with open(path, encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

_FALLBACK_DATA = _load_fallback_data()


# ---------------------------------------------------------------------------
# Gemini 클라이언트 초기화 (Google AI Studio 무료)
# ---------------------------------------------------------------------------
# ⚠️ [현황 2026-07-10] 실시간 LLM 쉬운 문장 재구성이 현재 동작하지 않음:
#   1) `google-genai` 패키지 미설치 → _get_client()가 None 반환 → 항상 _demo_restructure 폴백
#   2) 설령 설치해도 Gemini 무료 쿼터 소진(HTTP 429) → 호출 실패
#   현재 업로드 모드는 원문에 "[중급 수준 재구성]" 라벨만 붙는 폴백 상태(실제로 안 쉬워짐).
#
# ✅ [TODO: 쿼터 복구 후 SnowChat 경로로 재배선]
#   rag_engine.py가 성공적으로 쓰는 것과 동일한 HTTP 경로로 통일한다:
#     from .snowchat_client import is_snowchat_available, _call_llm_via_snowchat
#   _call_llm()이 genai.Client 대신 _call_llm_via_snowchat(model="gemini-2.0-flash", prompt=...)
#   를 호출하도록 교체하면, google-genai 패키지 없이도 동일 키로 실 LLM 재구성이 된다.
#   (교체 후 반드시 원문 != 재구성 텍스트인지 검증할 것)

def _get_client():
    """Gemini 클라이언트를 반환한다. 키가 없거나 패키지가 없으면 None."""
    try:
        from google import genai

        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key or api_key.startswith("your_"):
            return None
        return genai.Client(api_key=api_key)
    except ImportError:
        return None


# ---------------------------------------------------------------------------
# 데모 / Stub 재구성
# ---------------------------------------------------------------------------

_LEVEL_LABELS = {
    1: "초급",
    2: "초중급",
    3: "중급",
    4: "중고급",
    5: "전문가",
}


def _demo_restructure(text: str, level: int) -> str:
    """API 없이 동작하는 데모용 재구성."""
    # 1. 고품질 데모 캐시 데이터 매칭 시도
    if _FALLBACK_DATA and "chunks" in _FALLBACK_DATA:
        normalized_text = text.replace(" ", "").replace("\n", "")
        for entry in _FALLBACK_DATA["chunks"]:
            ref_text = entry["original_text"].replace(" ", "").replace("\n", "")
            if normalized_text in ref_text or ref_text in normalized_text:
                return entry["restructured_text"]

    # 2. 매칭 실패 시 단순 시뮬레이션
    label = _LEVEL_LABELS.get(level, "중급")
    sentences = re.split(r"(?<=[다요했됩습])[.]\s*|(?<=[.!?])\s+", text)
    simplified = " ".join(s.strip() for s in sentences if s.strip())
    return f"[{label} 수준 재구성] {simplified}"


# ---------------------------------------------------------------------------
# 단일 청크 LLM 호출
# ---------------------------------------------------------------------------

def _call_llm(
    client,
    chunk_text: str,
    level: int,
    domain: str,
    difficulty: float,
    term_count: int,
) -> tuple[str, str]:
    """
    Gemini API를 호출하여 텍스트를 재구성한다.

    Returns:
        (restructured_text, model_used)
    """
    from google.genai import types

    # 1번의 딜리버리 플랜에 따라 gemini-2.0-flash 사용
    model = "gemini-2.0-flash"
    prompt = build_summary_prompt(chunk_text, level, domain)

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SUMMARY_SYSTEM_PROMPT,
        ),
    )
    result = response.text.strip()
    return result, model


# ---------------------------------------------------------------------------
# 공개 API
# ---------------------------------------------------------------------------

def summarize_text(chunk: ChunkDict, user_literacy_level: int, domain: str = "일반") -> ChunkDict:
    """
    주어진 청크의 텍스트를 LLM(또는 Fallback)을 통해 요약한다.
    결과는 chunk["summary"] 에 저장된다.
    """
    start_time = time.time()
    original_text = chunk["original_text"]
    chunk_difficulty = chunk.get("difficulty", 3.0)
    term_count = len(chunk.get("terms", []))

    mode = os.getenv("CONTENT_REDUCER_MODE", "real").lower()
    demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
    client = _get_client()

    if mode == "stub" or demo_mode or client is None:
        generated_text = _demo_restructure(original_text, user_literacy_level)
        model = "demo_mode"
        latency = int((time.time() - start_time) * 1000)
    else:
        try:
            generated_text, model = _call_llm(
                client, original_text, user_literacy_level, domain, chunk_difficulty, term_count
            )
            latency = int((time.time() - start_time) * 1000)
        except Exception as e:
            latency = int((time.time() - start_time) * 1000)
            generated_text = _demo_restructure(original_text, user_literacy_level)
            model = f"fallback_on_error: {str(e)}"

    chunk["restructured_text"] = original_text
    chunk["summary"] = generated_text
    chunk["_meta"] = {
        "model_used": model,
        "summarizer_latency_ms": latency,
        "route_reason": get_routing_reason(chunk_difficulty, term_count, model),
    }
    return chunk
