"""Adapter for the Cognitive Care agent."""

from __future__ import annotations

from backend.app.agents.config import run_agent
from backend.app.agents.stubs.cognitive_care_stub import cognitive_care_stub
from backend.app.orchestrator.state import ReadingSessionState

# 실제 3번 모듈이 준비되면 real=<real_fn>을 채운다.
_REAL_IMPL = None


def run_cognitive_care(state: ReadingSessionState) -> ReadingSessionState:
    """Run the configured Cognitive Care implementation."""
    return run_agent("cognitive_care", state, stub=cognitive_care_stub, real=_REAL_IMPL)
