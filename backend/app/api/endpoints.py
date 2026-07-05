from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid
import json

from ..core.db import get_db
from ..core.redis import get_redis
from ..models.models import ReadingSession, ReadingEvent, User
from ..schemas.schemas import SessionStartRequest, SessionStartResponse, SessionFinishRequest, SessionFinishResponse
from ..orchestrator.state import create_initial_state
from ..orchestrator.graph import run_reading_session

router = APIRouter(prefix="/api/session", tags=["Sessions"])

@router.post("/start", response_model=SessionStartResponse)
async def start_session(req: SessionStartRequest, db: AsyncSession = Depends(get_db)):
    # 유저가 없으면 더미 유저 생성 (데모용)
    user_result = await db.execute(select(User).filter(User.id == req.user_id))
    user = user_result.scalars().first()
    if not user:
        new_user = User(id=req.user_id)
        db.add(new_user)
        await db.commit()

    session_id = f"s_{uuid.uuid4().hex[:8]}"
    
    new_session = ReadingSession(
        id=session_id,
        user_id=req.user_id,
        document_id=req.document_id
    )
    db.add(new_session)
    await db.commit()
    
    return SessionStartResponse(session_id=session_id, message="Session started successfully.")

@router.post("/{session_id}/finish", response_model=SessionFinishResponse)
async def finish_session(
    session_id: str, 
    req: SessionFinishRequest, 
    db: AsyncSession = Depends(get_db),
    # async generator dependency -> use simple getter or fastAPI Depends
):
    from ..core.redis import REDIS_URL
    import redis.asyncio as redis
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    
    try:
        # 1. DB에서 세션 조회
        result = await db.execute(select(ReadingSession).filter(ReadingSession.id == session_id))
        session = result.scalars().first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
            
        # 2. Redis에서 이벤트 가져오기
        redis_key = f"session:{session_id}:events"
        all_events_raw = await redis_client.lrange(redis_key, 0, -1)
        
        saved_count = 0
        state_events = []
        for raw_event in all_events_raw:
            event_dict = json.loads(raw_event)
            new_event = ReadingEvent(
                session_id=session_id,
                event_type=event_dict.get("type", "unknown"),
                timestamp_ms=event_dict.get("timestamp_ms", 0),
                metadata_json=event_dict
            )
            db.add(new_event)
            saved_count += 1
            
            # Orchestrator 상태 주입을 위한 이벤트 리스트 구성
            state_events.append({
                "type": event_dict.get("type", "unknown"),
                "timestamp_ms": event_dict.get("timestamp_ms", 0),
                "metadata": event_dict
            })
            
        # 3. 오케스트레이터(Role 1) 파이프라인 실행
        initial_state = create_initial_state(
            session_id=session_id,
            user_id=session.user_id,
            document_id=session.document_id,
            raw_text="Sample Document Text"
        )
        initial_state["reading_events"] = state_events
        final_state = run_reading_session(initial_state)

        # 4. 세션 정보 업데이트 (Orchestrator 최종 점수 반영)
        session.literacy_score = final_state.get("literacy_score", req.literacy_score)
        session.comprehension_score = final_state.get("comprehension_score", req.comprehension_score)
        session.engagement_score = final_state.get("engagement_score", req.engagement_score)
        
        await db.commit()
        
        # 4. Redis 캐시 비우기
        await redis_client.delete(redis_key)
        
        return SessionFinishResponse(
            session_id=session_id, 
            message="Session finished and flushed to PostgreSQL.",
            saved_events_count=saved_count
        )
    finally:
        await redis_client.aclose()
