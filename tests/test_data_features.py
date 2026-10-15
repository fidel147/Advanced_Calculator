import pandas as pd

from engine.data import correlation_matrix, dataset_summary, descriptive_statistics, search_rows


def test_dataset_metadata_and_statistics():
    frame = pd.DataFrame({
        "age": [20, 30, 40],
        "score": [1, 2, 3],
        "group": ["A", "B", "A"],
    })
    summary = dataset_summary(frame)
    assert summary["rows"] == 3
    assert summary["columns"] == 3
    assert summary["duplicate_rows"] == 0
    assert summary["memory_bytes"] > 0
    statistics = descriptive_statistics(frame)
    assert statistics.loc[statistics["column"] == "age", "median"].iloc[0] == 30
    assert correlation_matrix(frame, "spearman").shape == (2, 2)


def test_row_search_is_literal_and_case_insensitive():
    frame = pd.DataFrame({"name": ["Alpha", "beta"], "value": [1, 2]})
    assert len(search_rows(frame, "BETA")) == 1
    assert len(search_rows(frame, ".")) == 0
