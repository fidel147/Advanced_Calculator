import pandas as pd

from engine.data import describe_frame, group_summary, value_counts


def test_dataframe_analysis_helpers():
    frame = pd.DataFrame({
        "region": ["south", "north", "south"],
        "charges": [10, 20, 30],
    })
    assert set(describe_frame(frame)["column"]) == {"region", "charges"}
    assert value_counts(frame, "region")["count"].sum() == 3
    grouped = group_summary(frame, "region", "charges", "mean")
    assert grouped.iloc[0]["mean_charges"] == 20
