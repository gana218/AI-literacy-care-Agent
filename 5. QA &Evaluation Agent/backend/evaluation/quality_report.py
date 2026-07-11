def generate_quality_report(
    faithfulness: float,
    relevance: float,
    threshold: float
):

    overall_score = round(
        (faithfulness + relevance) / 2,
        2
    )

    return {
        "faithfulness": faithfulness,
        "relevance": relevance,
        "overall_score": overall_score,
        "threshold": threshold,
        "passed": overall_score >= threshold,
    }