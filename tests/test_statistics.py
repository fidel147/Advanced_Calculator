import pandas as pd

from engine.statistics import run_test


def test_inferential_results_include_interpretation_fields():
    frame = pd.DataFrame({
        "value": [10, 11, 9, 10, 12, 8],
        "group": ["a", "a", "a", "b", "b", "b"],
    })
    result = run_test(frame, "Independent t-test", "value", "group")
    assert "Hypothesis" in set(result["metric"])
    assert "p-value" in set(result["metric"])
    assert "Assumptions" in set(result["metric"])
