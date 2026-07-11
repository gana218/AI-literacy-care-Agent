from backend.evaluation.evaluation_pipeline import (
    run_evaluation_pipeline
)

from backend.evaluation.quality_report import (
    generate_quality_report
)


def evaluate_sample(sample=None):

    result = run_evaluation_pipeline(sample)

    report = generate_quality_report(
        faithfulness=result["faithfulness"],
        relevance=result["relevance"],
        threshold=result["threshold"]
    )

    return report