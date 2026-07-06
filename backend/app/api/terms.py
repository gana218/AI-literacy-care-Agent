from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import json
from pathlib import Path

router = APIRouter(prefix="/api/terms", tags=["Terms Lookup"])

_TERM_DICT_PATH = Path(__file__).resolve().parents[1] / "agents" / "real" / "term_dictionary.json"
_TERM_CACHE = None

def _load_terms() -> list[dict]:
    global _TERM_CACHE
    if _TERM_CACHE is None:
        try:
            data = json.loads(_TERM_DICT_PATH.read_text(encoding="utf-8"))
            _TERM_CACHE = data.get("terms", []) if isinstance(data, dict) else []
        except (OSError, ValueError):
            _TERM_CACHE = []
    return _TERM_CACHE

@router.get("/lookup")
async def lookup_term_api(word: str, sessionId: str | None = None, context: str | None = None):
    """
    단어 단건에 대한 무료 용어풀이 결과를 반환한다.
    term_dictionary.json (오프라인 사전) 활용.
    """
    if not word:
        raise HTTPException(status_code=400, detail="word is required")
        
    low = word.lower()
    for entry in _load_terms():
        names = [entry.get("term", "")] + list(entry.get("aliases", []))
        if any(n and n.lower() == low for n in names):
            return {
                "term": entry["term"],
                "definition": entry.get("definition", ""),
                "source": entry.get("source", ""),
                "faithfulnessScore": 1.0,
                "chunkId": ""
            }
            
    # 검색 실패 시 기본 응답 폴백
    return {
        "term": word,
        "definition": f"'{word}'에 대한 사전 뜻을 찾을 수 없습니다.",
        "source": "Local Fallback",
        "faithfulnessScore": 0.0,
        "chunkId": ""
    }
