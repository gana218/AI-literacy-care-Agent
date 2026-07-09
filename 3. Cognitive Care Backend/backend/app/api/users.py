from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..core.db import get_db
from ..models.models import ReadingSession, ReadingEvent, User

router = APIRouter(prefix="/api/user", tags=["User Data Management"])

@router.delete("/{user_id}/data")
async def delete_user_data(user_id: str, db: AsyncSession = Depends(get_db)):
    """
    ADR-002: 익명 사용자 데이터 파기 요청 (세션 및 이벤트 일괄 삭제)
    """
    user_result = await db.execute(select(User).filter(User.id == user_id))
    user = user_result.scalars().first()
    
    if not user:
        return {"status": "success", "message": f"User {user_id} not found or already deleted."}
        
    # 세션 조회
    sessions_result = await db.execute(select(ReadingSession).filter(ReadingSession.user_id == user_id))
    sessions = sessions_result.scalars().all()
    session_ids = [s.id for s in sessions]
    
    # 해당 세션의 모든 이벤트 삭제
    if session_ids:
        for sid in session_ids:
            events_result = await db.execute(select(ReadingEvent).filter(ReadingEvent.session_id == sid))
            events = events_result.scalars().all()
            for ev in events:
                await db.delete(ev)
            
        for s in sessions:
            await db.delete(s)
            
    await db.delete(user)
    await db.commit()
    
    return {"status": "success", "message": f"Data for user {user_id} deleted successfully."}

@router.get("/{user_id}/growth")
async def get_user_growth(user_id: str, db: AsyncSession = Depends(get_db)):
    """
    Returns the user's detailed growth report data (weekly/monthly).
    Currently returns dummy data.
    """
    return {
        "weekly": {
            "radarData": [
                {"subject": '어휘력', "before": 62, "after": 84},
                {"subject": '독해 속도', "before": 55, "after": 78},
                {"subject": '정독율', "before": 70, "after": 88},
                {"subject": '추론 능력', "before": 65, "after": 80},
                {"subject": '집중 유지', "before": 60, "after": 92},
            ],
            "activityData": [
                {"label": '월', "time": 15, "xp": 120},
                {"label": '화', "time": 22, "xp": 180},
                {"label": '수', "time": 12, "xp": 90},
                {"label": '목', "time": 28, "xp": 240},
                {"label": '금', "time": 18, "xp": 150},
                {"label": '토', "time": 35, "xp": 320},
                {"label": '일', "time": 42, "xp": 380},
            ],
            "words": [
                {"word": '기각 (Dismissal)', "meaning": '소송이나 신청이 법적 요건을 갖추지 못했거나 이유가 없다고 돌려보내는 일.', "level": '상', "status": 'completed'},
                {"word": '양형 (Sentencing)', "meaning": '재판관이 형벌의 정도를 결정하는 일.', "level": '중', "status": 'completed'},
                {"word": '귀책사유 (Imputable Reason)', "meaning": '법적 책임을 지울 수 있는 원인이나 과실.', "level": '상', "status": 'review'},
                {"word": '인과관계 (Causality)', "meaning": '원인과 결과 사이의 관계.', "level": '하', "status": 'completed'},
            ]
        },
        "monthly": {
            "radarData": [
                {"subject": '어휘력', "before": 58, "after": 89},
                {"subject": '독해 속도', "before": 50, "after": 82},
                {"subject": '정독율', "before": 65, "after": 91},
                {"subject": '추론 능력', "before": 60, "after": 85},
                {"subject": '집중 유지', "before": 55, "after": 94},
            ],
            "activityData": [
                {"label": '1주차', "time": 78, "xp": 680},
                {"label": '2주차', "time": 92, "xp": 820},
                {"label": '3주차', "time": 110, "xp": 1020},
                {"label": '4주차', "time": 145, "xp": 1350},
            ],
            "words": [
                {"word": '개정 (Revision)', "meaning": '이미 정하였던 법령이나 규칙 따위를 고쳐서 다시 정함.', "level": '하', "status": 'completed'},
                {"word": '지적재산권 (IP)', "meaning": '인간의 지적 창작물에 대해 법이 부여한 권리.', "level": '중', "status": 'completed'},
                {"word": '추상적 (Abstract)', "meaning": '구체적이지 않고 일반적이거나 관념적인 것.', "level": '하', "status": 'completed'},
                {"word": '기속력 (Binding Force)', "meaning": '법원이나 행정기관이 스스로 내린 결정에 구속되는 효력.', "level": '상', "status": 'review'},
            ]
        }
    }
