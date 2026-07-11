from backend.evaluation.evaluation_pipeline import (
    run_evaluation_pipeline
)

def test_full_pipeline():

    result = run_evaluation_pipeline()

    assert result["faithfulness"] >= 0
    assert result["relevance"] >= 0
    assert result["average_score"] >= 0