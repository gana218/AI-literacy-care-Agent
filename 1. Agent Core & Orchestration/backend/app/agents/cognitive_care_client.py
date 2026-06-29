"""Adapter for the Cognitive Care agent."""

from __future__ import annotations

from backend.app.agents.config import run_agent
from backend.app.agents.real.cognitive_care_service import (
    calculate_focus_score,
    determine_intervention,
)
from backend.app.agents.stubs.cognitive_care_stub import cognitive_care_stub
from backend.app.orchestrator.state import ReadingSessionState


def _cognitive_care_real(state: ReadingSessionState) -> ReadingSessionState:
    """3번 실제 모듈을 ReadingSessionState 계약으로 매핑한다.

    3번 `cognitive_care_service`는 순수 함수만 제공하므로, reading_events를
    넘겨 focus_score를 받고 계약 필드(focus/engagement/intervention_needed)를 채운다.

    주의:
    - 3번 모듈은 engagement_score를 산출하지 않는다. 스텁과 동일한 관례로
      engagement_score = focus_score 로 둔다(별도 신호가 생기면 교체).
    - 최종 intervention 명령(level/type/message)은 orchestrator의 routing.py가
      단독 결정한다. 여기서는 intervention_needed 플래그까지만 채운다.
    """
    events = state.get("reading_events", [])
    focus_score = calculate_focus_score(events)
    needed, _level, _message = determine_intervention(focus_score)

    state["focus_score"] = focus_score
    state["engagement_score"] = focus_score
    state["intervention_needed"] = needed
    return state


# 실제 3번 모듈 연결 완료 — LITERACY_COGNITIVE_CARE_IMPL=real 로 전환.
_REAL_IMPL = _cognitive_care_real


def run_cognitive_care(state: ReadingSessionState) -> ReadingSessionState:
    """Run the configured Cognitive Care implementation."""
    return run_agent("cognitive_care", state, stub=cognitive_care_stub, real=_REAL_IMPL)
