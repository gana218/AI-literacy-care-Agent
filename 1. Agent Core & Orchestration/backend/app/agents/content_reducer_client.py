"""Adapter for the Content Reducer agent."""

from __future__ import annotations

from backend.app.agents.config import run_agent
from backend.app.agents.stubs.content_reducer_stub import content_reducer_stub
from backend.app.orchestrator.state import ReadingSessionState

# 실제 2번 모듈이 준비되면 real=<real_fn>을 채운다.
_REAL_IMPL = None


def run_content_reducer(state: ReadingSessionState) -> ReadingSessionState:
    """Run the configured Content Reducer implementation."""
    return run_agent("content_reducer", state, stub=content_reducer_stub, real=_REAL_IMPL)
