import hashlib

def generate_ox_quiz(summary: str, paragraph: str, chunk_id: str, session_id: str) -> dict:
    """
    문단 요약(summary)과 원문(paragraph)을 기반으로 O/X 퀴즈를 생성합니다.
    
    내부 동작:
    - LLM(Claude/Gemini 등)을 호출하여 O/X 퀴즈를 출제.
    - LLM 실패 시 또는 키가 없을 경우 chunk_id 해시 기반 결정론적 폴백 로직 수행.
    """
    quiz_id = f"quiz_{session_id}_{chunk_id}"
    
    # TODO: LLM 연동 
    # 현재는 요청사항 5-1의 결정론적 폴백 로직을 우선 적용합니다.
    h_val = int(hashlib.md5(chunk_id.encode('utf-8')).hexdigest(), 16)
    is_even = (h_val % 2 == 0)
    
    if is_even:
        statement = summary if summary else "본문의 내용을 올바르게 요약했습니다."
        answer = True
        explanation = "요약과 일치합니다."
    else:
        statement = f"이 문단은 다음 내용과 반대되거나 관련이 적습니다: {summary}" if summary else "본문의 내용과 다릅니다."
        answer = False
        explanation = "원문의 핵심 서술어/수치 등을 반대로 왜곡한 진술입니다."

    # 프론트(apps/web QuizData)·확장 공용 shape (role-1 canonical과 정렬).
    #   question: QuizCard가 렌더하는 진술문(= statement)
    #   options: ["O","X"] → QuizCard가 O/X 2버튼 모드로 렌더
    #   answer/explanation: 서버 채점용(프론트 payload에선 노출 금지)
    return {
        "quizId": quiz_id,
        "type": "ox",
        "question": statement,
        "statement": statement,
        "options": ["O", "X"],
        "answer": answer,
        "explanation": explanation,
        "sourceChunkId": chunk_id
    }


def select_quiz_for_state(state: dict) -> dict | None:
    """
    현재 사용자 상태(방금 읽던 position)를 바탕으로 미출제 퀴즈를 선택합니다.
    """
    quizzes = state.get("quizzes", {})
    if not quizzes:
        return None
        
    asked_quiz_ids = state.get("asked_quiz_ids", [])
    events = state.get("reading_events", [])
    chunks = state.get("chunks", [])
    
    if not events or not chunks:
        return None
        
    # 가장 최근 이벤트의 position 추출
    latest_position = events[-1].get("position", 0.0)
    if latest_position is None:
        latest_position = 0.0
        
    # 방금 읽은 문단 인덱스 추정
    chunk_index = round(latest_position * (len(chunks) - 1))
    chunk_index = max(0, min(chunk_index, len(chunks) - 1))
    
    target_chunk_id = chunks[chunk_index].get("chunk_id")
    if not target_chunk_id:
        return None
        
    quiz = quizzes.get(target_chunk_id)
    if not quiz:
        return None
        
    # 이미 출제된 퀴즈인지 확인 (1세션 1문단 1회)
    if quiz["quizId"] in asked_quiz_ids:
        return None
        
    return quiz
