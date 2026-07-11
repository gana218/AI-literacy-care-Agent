from backend.evaluation.metrics import (
    calculate_faithfulness_score,
    calculate_relevance_score,
    calculate_average,
    is_passed,
)


# 단어 중첩 기반 휴리스틱 평가 기준
# 절대 품질 점수가 아니라 골든셋 내 상대 비교 및 회귀 감지용
PASS_THRESHOLD = 0.30


def run_evaluation(sample: dict) -> dict:
    """
    Golden Dataset 한 개를 평가한다.
    """

    raw_text = sample.get("raw_text", "")
    quiz = sample.get("expected_quiz", {})

    if isinstance(quiz, dict):
        question = quiz.get("question", "")
    else:
        question = str(quiz)

    expected_answer = sample.get("expected_answer", "")

    faithfulness = calculate_faithfulness_score(
        expected=raw_text,
        actual=expected_answer,
    )

    relevance = calculate_relevance_score(
        question=question,
        answer=expected_answer,
    )

    average_score = calculate_average(
        [faithfulness, relevance]
    )

    return {
        "faithfulness": faithfulness,
        "relevance": relevance,
        "average_score": average_score,
        "threshold": PASS_THRESHOLD,
        "passed": is_passed(
            average_score,
            threshold=PASS_THRESHOLD,
        ),
    }


def run_evaluation_pipeline(sample=None):
    """
    테스트용 평가 파이프라인
    """

    if sample is None:
        sample = {
            "raw_text": "머신러닝은 데이터를 통해 학습한다.",
            "expected_quiz": {
                "question": "머신러닝은 무엇을 통해 학습하는가?"
            },
            "expected_answer": "머신러닝은 데이터를 통해 학습한다.",
        }

    return run_evaluation(sample)


def run_evaluation_from_state(state: dict) -> dict:
    """
    Orchestrator의 ReadingSessionState를 받아
    QA 평가를 수행한다.
    """

    quiz_result = state.get("quiz_result", {})

    if isinstance(quiz_result, dict):
        expected_quiz = {
            "question": quiz_result.get("question", "")
        }
    else:
        expected_quiz = {
            "question": str(quiz_result)
        }

    sample = {
        "raw_text": state.get("raw_text", ""),
        "expected_quiz": expected_quiz,
        "expected_answer": state.get("simplified_text", ""),
    }

    report = run_evaluation(sample)

    report["session_id"] = state.get("session_id")
    report["document_id"] = state.get("document_id")
    report["has_trace"] = len(state.get("trace", [])) > 0
    report["has_errors"] = len(state.get("errors", [])) > 0

    return report