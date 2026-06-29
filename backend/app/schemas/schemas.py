from pydantic import BaseModel
from typing import Optional

class SessionStartRequest(BaseModel):
    userId: str
    articleId: str

class SessionStartResponse(BaseModel):
    sessionId: str
    article: dict
    wsEndpoint: str

class SessionFinishRequest(BaseModel):
    literacy_score: Optional[float] = None
    comprehension_score: Optional[float] = None
    engagement_score: Optional[float] = None

class SessionFinishResponse(BaseModel):
    session_id: str
    message: str
    saved_events_count: int
