"""3번(백엔드/Cognitive Care) 실제 구현 — 원본 그대로 이식(re-vendored).

출처: naaaayeonn/AI-literacy-care-Agent @ main
      `3. Cognitive Care Backend/backend/app/services/cognitive_care.py`
      (재이식 2026-07-11 · sha256 e5d0df88…)

이 파일은 팀원 3번이 작성한 순수 함수를 이식한 것이다.
오케스트레이터 계약(ReadingSessionState)으로의 변환은
`backend/app/agents/cognitive_care_client.py`의 어댑터가 담당한다.

⚠️ 원본과의 차이(1번 로컬 수정, 2026-07-11):
  스크롤 스키밍 감점에서 `간격 < 250ms` 조건을 제거하고 velocity(>임계)만 남겼다.
  tracker 스로틀(120ms) 탓에 정상 스크롤도 간격 조건에 상시 걸려 오검출을 냈다.
  → 3번 원본에도 동일 반영 후 재이식하면 이 divergence가 사라진다.

집중도 규칙:
- **최근 12개 이벤트 창(window)** 으로 "현재" 집중도를 산정(누적 아님 → 실시간 반응)
- blur: -20 + min(이탈초 × 2, 15)
- 스키밍 스크롤: velocity > 임계(디폴트 1.5 px/ms) → -8
- pause(무동작): -18 · 과도한 dwell(한 단락 20초+): -12
- 스크롤 속도(velocity)는 확장 tracker가 event.velocity(px/ms)로, 웹은
  metadata.payload.scrollVelocity로 공급한다.
- 개입 컷오프 75/50/30 (1번 routing과 일치)
"""

from typing import Any, Dict, List, Tuple


def _scroll_velocity(event: Dict[str, Any]) -> float:
    """스크롤 속도(px/s)를 이벤트에서 정규화해 읽는다.
    - 확장(tracker.js): 최상위 velocity 미제공(대신 duration_ms=스크롤 간격)
    - 웹(ReadingPane): metadata.payload.scrollVelocity 에 담겨 옴
    """
    v = event.get("velocity")
    if v is None:
        meta = event.get("metadata") or {}
        payload = meta.get("payload") if isinstance(meta, dict) else None
        if isinstance(payload, dict):
            v = payload.get("scrollVelocity")
    try:
        return float(v) if v is not None else 0.0
    except (TypeError, ValueError):
        return 0.0


def _personalized_scroll_threshold(baseline: Dict[str, Any] = None, difficulty_score: float = None) -> float:
    """온보딩 캘리브레이션 + 글 난이도로 개인화한 스키밍 임계값(px/ms).

    개인의 "난이도별 편안한 읽기 속도" 직선을 두 캘리브레이션 점(easy/hard)으로 세우고,
    지금 글 난이도 D에서의 예상 속도 × 여유계수 K를 임계값으로 쓴다.
    → 어려운 글일수록 임계값↓(일찍 스키밍 판정), 쉬운 글일수록 임계값↑(과감점 방지).
    온보딩 2점만 있을 땐 인구집단 기본값(1.5)과 신뢰도 가중 블렌딩한다(과적합 방지).

    baseline 계약: {easy, hard, d_easy(기본20), d_hard(기본75), n_sessions}
    """
    DEFAULT = 1.5   # 인구집단 기본 임계(px/ms)
    FLOOR = 0.4     # 하한(너무 예민해지지 않게)
    K = 1.8         # 편안한 속도 대비 스키밍으로 볼 배수
    if not baseline:
        return DEFAULT
    v_easy = baseline.get("easy")
    v_hard = baseline.get("hard")
    if v_easy is None or v_hard is None:
        return DEFAULT
    try:
        v_easy = float(v_easy)
        v_hard = float(v_hard)
        d_easy = float(baseline.get("d_easy", 20.0))
        d_hard = float(baseline.get("d_hard", 75.0))
        D = float(difficulty_score) if difficulty_score is not None else (d_easy + d_hard) / 2.0
    except (TypeError, ValueError):
        return DEFAULT

    # 개인 속도-난이도 선형 예측(보통 어려울수록 느리게 읽어 v_easy > v_hard).
    if d_hard != d_easy:
        slope = (v_hard - v_easy) / (d_hard - d_easy)
        expected = v_easy + slope * (D - d_easy)
    else:
        expected = (v_easy + v_hard) / 2.0
    expected = max(0.1, expected)
    personal = max(FLOOR, expected * K)

    # 신뢰도 블렌딩: rolling update 세션 수(n_sessions)가 쌓일수록 개인값을 더 신뢰.
    try:
        n = int(baseline.get("n_sessions", 0) or 0)
    except (TypeError, ValueError):
        n = 0
    w = min(1.0, 0.5 + 0.1 * n)  # 온보딩만(n=0) → 0.5, 5세션 누적 → 1.0
    threshold = w * personal + (1.0 - w) * DEFAULT
    return max(FLOOR, threshold)


def calculate_focus_score(events: List[Dict[str, Any]], baseline: Dict[str, Any] = None, difficulty_score: float = None) -> float:
    """
    행동 이벤트 리스트를 분석하여 0~100 사이의 실시간 집중도(Focus Score)를 계산합니다.

    "지금" 얼마나 몰입해 읽고 있는지를 나타내도록 **최근 이벤트 창(window)** 기준으로 산정한다.
    (누적 합산은 세션이 길어질수록 무조건 낮아지고, 최근 행동 변화에 둔감해지므로 사용하지 않음)

    [조작적 정의 (Operational Definition) & 측정 한계]
      - "집중" 상태는 브라우저 탭이 포커스되어 있고, 스크롤 속도가 정상 범주이며, 단락 체류가 적절한 상태를 뜻함.
      - 측정 한계: 의도적인 용어 검색 이탈과 단순 한눈팔기(blur)를 엄밀히 구분하기 어렵기 때문에
        모든 이탈은 blur로 단순화하여 측정함. 멍때리기는 12초 이상 무동작(pause)으로 간접 감지함.

    감점 규칙(집중 저하 신호):
      - blur(화면 이탈)         : 크게 감점 (이탈 시간 비례 추가)
      - 빠른 스크롤(스키밍)      : 스크롤 속도가 임계(디폴트 1.5 px/ms, 개인 기준선의 2.0배) 초과 시 감점
      - pause(무동작·멍/이탈)    : 감점
      - 과도한 dwell(한 단락 20초+ 정체) : 감점
    """
    if not events:
        return 100.0

    # 최근 행동 위주로 현재 집중도를 산정 (실시간 반응성 확보)
    recent = events[-12:]
    score = 100.0

    # 7/13: 난이도-인지 개인화 스키밍 임계값. 온보딩 캘리브레이션(easy/hard) + 글 난이도(2번)로
    # "이 사람이·이 난이도 글을 얼마나 빨리 넘기면 안 읽는 것인가"를 판정. (기존 avg×2.0 마법값 폐기)
    scroll_threshold = _personalized_scroll_threshold(baseline, difficulty_score)

    for event in recent:
        etype = event.get("type")

        if etype == "blur":
            duration = event.get("duration_ms")
            if duration is None:
                duration = 3000
            score -= 20.0 + min((duration / 1000.0) * 2.0, 15.0)

        elif etype == "scroll":
            velocity = _scroll_velocity(event)
            # 스키밍 판정은 스크롤 속도(velocity)로만 한다. 간격(<250ms) 조건은
            # tracker 스로틀(120ms) 탓에 정상 스크롤도 상시 걸려 오검출을 냈다(1번 수정).
            too_fast_velocity = velocity > scroll_threshold
            if too_fast_velocity:
                # 스키밍(비정상적으로 빠른 스크롤): 실제로 읽지 않는 신호
                # 1~2회는 소폭이지만, 지속되면 최근 창(window)을 채워 급격히 하락한다.
                score -= 8.0

        elif etype == "pause":
            # 무동작이 임계 시간 이상 지속(멍때림·이탈)
            score -= 18.0

        elif etype == "dwell":
            meta = event.get("metadata") or {}
            payload = meta.get("payload") if isinstance(meta, dict) else None
            dwell_ms = None
            if isinstance(payload, dict):
                dwell_ms = payload.get("dwellMs")
            if dwell_ms is None:
                dwell_ms = event.get("duration_ms") or 0
            # 한 단락에 지나치게 오래 머무름 = 집중이 흐트러진 정체 상태
            if dwell_ms > 20000:
                score -= 12.0

        # focus(복귀)·정상 스크롤·적정 dwell 은 감점하지 않음

    return round(max(0.0, min(100.0, score)), 1)

def determine_intervention(focus_score: float) -> Tuple[bool, str, str]:
    """
    Focus Score에 따라 개입(Intervention) 여부 및 피드백 메시지를 결정합니다.
    """
    if focus_score >= 75.0:
        return False, "none", ""
    elif 50.0 <= focus_score < 75.0:
        return True, "soft", "핵심 문장을 다시 한번 살펴볼까요? 📌"
    elif 30.0 <= focus_score < 50.0:
        return True, "medium", "잠깐! 조금 쉬었다가 다시 읽어보는 건 어때요? ☕"
    else:
        return True, "hard", "집중이 필요해요! 간단한 퀴즈로 내용을 확인해봐요! 📝"
