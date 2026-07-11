from typing import Dict


def compare_evaluation_results(
    baseline: Dict[str, float],
    current: Dict[str, float],
    tolerance: float = 0.05,
) -> dict:
    """
    Promptfoo 미연결 환경에서 사용하는 로컬 회귀 비교 함수.

    baseline과 current의 Faithfulness, Relevance,
    Overall Score를 비교하여 성능 저하 여부를 판단한다.

    tolerance보다 큰 점수 하락이 발생하면 regression으로 판정한다.
    """

    metric_names = [
        "faithfulness",
        "relevance",
        "overall_score",
    ]

    differences = {}
    regressions = []

    for metric in metric_names:
        baseline_score = float(baseline.get(metric, 0.0))
        current_score = float(current.get(metric, 0.0))

        difference = round(
            current_score - baseline_score,
            4,
        )

        differences[metric] = difference

        if difference < -tolerance:
            regressions.append(metric)

    return {
        "evaluator": "local_regression_check",
        "promptfoo_enabled": False,
        "tolerance": tolerance,
        "differences": differences,
        "regression_detected": len(regressions) > 0,
        "regressed_metrics": regressions,
        "note": (
            "실제 Promptfoo 실행이 아닌 로컬 점수 비교 결과입니다."
        ),
    }