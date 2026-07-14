from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from ..agents.content_reducer.rag_engine import lookup_term

router = APIRouter(prefix="/api/terms", tags=["Terms Lookup"])


class TermLookupRequest(BaseModel):
    word: str
    sessionId: Optional[str] = None
    context: Optional[str] = None  # 1번 팀 연동: LLM 실시간 유추용 문맥 필드


# ── POST (신규: 1번 팀 RAG 고도화 연동) ──────────────────────────────────────
@router.post("/lookup")
async def lookup_term_post(req: TermLookupRequest):
    """
    단어 단건에 대한 용어풀이 결과를 반환한다. (POST 방식)
    1번 팀 RAG 고도화(우리말샘 API + LLM 실시간 유추) 연동 완료.
    context 필드에 드래그한 단어 주변 문장을 담아 보내면 LLM 유추 정확도가 크게 향상됩니다.
    """
    word = req.word.strip()
    if not word:
        raise HTTPException(status_code=400, detail="word is required")

    try:
        t = lookup_term(word, req.context)
        
        # 실시간 단어장 연동을 위해 lookup 이벤트 캐시에 기록 (세션 종료 시 DB 저장)
        if req.sessionId:
            try:
                import time
                import json
                from ..core.redis import get_redis
                redis_client = await get_redis()
                lookup_ev = {
                    "type": "lookup",
                    "timestamp_ms": int(time.time() * 1000),
                    "term": word,
                    "definition": t["definition"],
                    "source": t["source"]
                }
                await redis_client.rpush(f"session:{req.sessionId}:events", json.dumps(lookup_ev))
            except Exception as _ev_err:
                pass

        return {
            "term": t["term"],
            "definition": t["definition"],
            "source": t["source"],
            "faithfulnessScore": t.get("faithfulness_score", 0.0),
            "faithfulness_score": t.get("faithfulness_score", 0.0),
            "chunkId": t.get("chunk_id", ""),
            "chunk_id": t.get("chunk_id", ""),
            "_meta": t.get("_meta", {"tried": [], "errors": {}}),
        }
    except Exception as e:
        return {
            "term": word,
            "definition": f"'{word}'에 대한 사전 뜻을 찾을 수 없습니다. ({str(e)})",
            "source": "Local Fallback",
            "faithfulnessScore": 0.0,
            "faithfulness_score": 0.0,
            "chunkId": "",
            "chunk_id": "",
        }


# ── GET (하위 호환 유지) ──────────────────────────────────────────────────────
@router.get("/lookup")
async def lookup_term_get(word: str, sessionId: Optional[str] = None, context: Optional[str] = None):
    """
    단어 단건에 대한 용어풀이 결과를 반환한다. (GET 방식 - 하위 호환 유지)
    신규 연동은 POST 방식을 사용해 주세요.
    """
    if not word:
        raise HTTPException(status_code=400, detail="word is required")

    try:
        t = lookup_term(word.strip(), context)
        return {
            "term": t["term"],
            "definition": t["definition"],
            "source": t["source"],
            "faithfulnessScore": t.get("faithfulness_score", 0.0),
            "faithfulness_score": t.get("faithfulness_score", 0.0),
            "chunkId": t.get("chunk_id", ""),
            "chunk_id": t.get("chunk_id", ""),
            "_meta": t.get("_meta", {"tried": [], "errors": {}}),
        }
    except Exception as e:
        return {
            "term": word,
            "definition": f"'{word}'에 대한 사전 뜻을 찾을 수 없습니다. ({str(e)})",
            "source": "Local Fallback",
            "faithfulnessScore": 0.0,
            "faithfulness_score": 0.0,
            "chunkId": "",
            "chunk_id": "",
        }
