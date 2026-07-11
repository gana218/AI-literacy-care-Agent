from backend.evaluation.metrics import (
    calculate_faithfulness_score,
    calculate_relevance_score,
    calculate_average,
)


def evaluate_with_local_heuristic(
    raw_text: str,
    question: str,
    answer: str,
) -> dict:
    """
    RAGAS 미연결 환경에서 사용하는 로컬 휴리스틱 평가 함수.

    현재 구현은 실제 RAGAS 라이브러리나 LLM Judge를 호출하지 않는다.
    원문-답변, 질문-답변의 단어 중첩을 이용해
    Faithfulness와 Relevance를 근사 계산한다.

    향후 실제 RAGAS를 도입할 경우 이 함수 내부를 교체할 수 있다.
    """

    faithfulness = calculate_faithfulness_score(
        expected=raw_text,
        actual=answer,
    )

    relevance = calculate_relevance_score(
        question=question,
        answer=answer,
    )

    average_score = calculate_average(
        [faithfulness, relevance]
    )

    return {
        "evaluator": "local_heuristic",
        "ragas_enabled": False,
        "faithfulness": faithfulness,
        "relevance": relevance,
        "average_score": average_score,
        "note": (
            "실제 RAGAS가 아닌 단어 중첩 기반 로컬 휴리스틱 결과입니다."
        ),
    }