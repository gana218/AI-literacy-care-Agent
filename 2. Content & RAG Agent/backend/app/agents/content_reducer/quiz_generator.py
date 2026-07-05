"""
quiz_generator.py — 문맥 맞춤형 퀴즈 생성기 (M2)

집중도 저하 등의 개입 상황이 발생했을 때,
사용자가 읽은 청크의 텍스트(context)를 기반으로 내용 이해도를 평가하는 4지선다 퀴즈를 생성한다.

설계 요구사항:
  1. LLM을 사용하여 문맥 맞춤형 퀴즈 생성
  2. 퀴즈 형식 검증 (4개 선택지, correct_option 1~4 범위, explanation 존재)
  3. 실패 시 Fallback 퀴즈 반환 (fallbacks.py 이용)
  4. Real, Stub, Demo 모드 지원
"""
from __future__ import annotations

import json
import os
import re

from backend.app.agents.content_reducer.contracts import QuizDict, QuizGenerationRequest
from backend.app.agents.content_reducer.fallbacks import fallback_quiz
from backend.app.agents.content_reducer.prompts import QUIZ_SYSTEM_PROMPT, build_quiz_prompt

# ---------------------------------------------------------------------------
# 환경 설정
# ---------------------------------------------------------------------------

_MODE = os.getenv("CONTENT_REDUCER_MODE", "real").lower()
_DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"


# ---------------------------------------------------------------------------
# Anthropic 클라이언트 로더
# ---------------------------------------------------------------------------

def _get_client():
    """Anthropic 클라이언트를 반환한다."""
    try:
        import anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key or api_key.startswith("your_"):
            return None
        return anthropic.Anthropic(api_key=api_key)
    except ImportError:
        return None


# ---------------------------------------------------------------------------
# 퀴즈 유효성 검사 (Validation)
# ---------------------------------------------------------------------------

def validate_quiz(quiz: dict) -> bool:
    """
    생성된 퀴즈의 구조가 QuizDict 계약 요건을 충족하는지 검증한다.

    검증 조건:
      - question 필드가 존재하고 문자열이어야 함
      - options 필드가 존재하고 4개의 선택지를 담은 리스트여야 함
      - correct_option 필드가 존재하고 1~4 범위의 정수여야 함
      - explanation 필드가 존재하고 비어있지 않은 문자열이어야 함
    """
    try:
        if not isinstance(quiz.get("question"), str) or not quiz["question"].strip():
            return False
        
        options = quiz.get("options")
        if not isinstance(options, list) or len(options) != 4:
            return False
        for opt in options:
            if not isinstance(opt, str) or not opt.strip():
                return False
                
        correct = quiz.get("correct_option")
        # 1-indexed (1, 2, 3, 4) 정수인지 확인
        if not isinstance(correct, int) or correct not in [1, 2, 3, 4]:
            return False
            
        if not isinstance(quiz.get("explanation"), str) or not quiz["explanation"].strip():
            return False
            
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# 데모/시뮬레이션용 퀴즈 생성 (API 미호출)
# ---------------------------------------------------------------------------

def _generate_demo_quiz(chunk_id: str, context: str) -> QuizDict:
    """API 호출 없이 본문 키워드를 이용해 적절한 데모용 퀴즈를 자동 생성한다."""
    # 본문에서 핵심 키워드 검색 시도
    keywords = ["인공지능", "LLM", "RAG", "레이턴시", "메타인지", "문해력", "인지부하", "임베딩"]
    found = "본문 내용"
    for kw in keywords:
        if kw in context:
            found = kw
            break

    return QuizDict(
        chunk_id=chunk_id,
        question=f"본문에서 설명된 '{found}'의 주요 내용과 가장 일치하는 설명은 무엇인가요?",
        options=[
            f"1. {found}은 교육 발달에 아무런 영향을 미치지 않는다.",
            f"2. {found}의 개념을 명확히 이해하고 활용하여 문해력을 높일 수 있다.",
            f"3. {found}은 오직 컴퓨터 전공자만 이해할 수 있는 전문 지식이다.",
            f"4. {found}은 시스템 지연 시간을 오히려 증가시키는 주요 원인이다."
        ],
        correct_option=2,
        explanation=f"본문 문맥상 '{found}' 관련 내용은 독자의 학습 효율을 높이고 문해력을 돕는 용도 또는 특징으로 설명하고 있으므로 2번이 가장 올바른 설명입니다."
    )


# ---------------------------------------------------------------------------
# 공개 API
# ---------------------------------------------------------------------------

def generate_quiz(chunk_id: str, context: str) -> QuizDict:
    """
    주어진 텍스트 문맥을 분석하여 난이도와 일치하는 독해력 확인 퀴즈를 생성한다.

    Args:
        chunk_id: 문제를 생성할 청크 식별자
        context: 재구성된 청크 텍스트

    Returns:
        규격화된 QuizDict (실패 시 fallback_quiz 반환)
    """
    if not context or not context.strip():
        return fallback_quiz(chunk_id)

    # 1. Stub 또는 Demo 모드일 경우 API 없이 시뮬레이션
    if _MODE == "stub" or _DEMO_MODE:
        return _generate_demo_quiz(chunk_id, context)

    # 2. Anthropic 클라이언트 확인
    client = _get_client()
    if client is None:
        # API 키가 없으면 데모용 퀴즈 반환
        return _generate_demo_quiz(chunk_id, context)

    try:
        # 퀴즈 생성에는 Haiku 모델을 경량으로 사용 (프롬프트 비용 및 레이턴시 단축)
        model = os.getenv("QUIZ_GENERATOR_MODEL", "claude-haiku-4-5")
        prompt = build_quiz_prompt(context)

        response = client.messages.create(
            model=model,
            max_tokens=1024,
            system=QUIZ_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

        raw_content = response.content[0].text.strip()
        
        # JSON 블록 추출 파싱 ({ 로 시작해서 } 로 끝나는 부분 매칭)
        json_match = re.search(r"\{.*\}", raw_content, re.DOTALL)
        if json_match:
            quiz_data = json.loads(json_match.group(0))
        else:
            quiz_data = json.loads(raw_content)

        # 퀴즈 유효성 검사 실행
        if validate_quiz(quiz_data):
            return QuizDict(
                chunk_id=chunk_id,
                question=quiz_data["question"],
                options=quiz_data["options"],
                correct_option=quiz_data["correct_option"],
                explanation=quiz_data["explanation"]
            )
        else:
            print(f"[quiz_generator] WARNING: 생성된 퀴즈의 유효성 검사 실패. Fallback 적용. Raw: {raw_content}")
            return fallback_quiz(chunk_id)

    except Exception as exc:
        print(f"[quiz_generator] 퀴즈 생성 도중 예외 발생, fallback_quiz를 반환합니다. 원인: {exc}")
        return fallback_quiz(chunk_id)
