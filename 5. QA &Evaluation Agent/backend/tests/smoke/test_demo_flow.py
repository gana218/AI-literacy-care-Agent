from backend.evaluation.evaluation_runner import (
    evaluate_sample
)


def test_demo_environment_ready():

    report = evaluate_sample()

    assert "faithfulness" in report
    assert "relevance" in report
    assert "overall_score" in report
    assert isinstance(report["passed"], bool)