"""Inferential statistics helpers with explicit assumptions and readable results."""

import numpy as np
import pandas as pd
from scipy import stats


def _numeric(frame, column):
    if column not in frame.columns:
        raise ValueError("Choose a numeric column")
    values = pd.to_numeric(frame[column], errors="coerce").dropna()
    if len(values) < 2:
        raise ValueError("The selected column needs at least two numeric values")
    return values


def _result(test, hypothesis, statistic, p_value, assumptions, confidence_interval=None):
    rows = [
        ("Test", test),
        ("Hypothesis", hypothesis),
        ("Statistic", round(float(statistic), 6)),
        ("p-value", round(float(p_value), 6)),
        ("Significance", "Reject H0 at alpha=0.05" if p_value < 0.05 else "Do not reject H0 at alpha=0.05"),
        ("Assumptions", assumptions),
    ]
    if confidence_interval is not None:
        rows.append(("95% confidence interval", f"[{confidence_interval[0]:.6g}, {confidence_interval[1]:.6g}]"))
    return pd.DataFrame(rows, columns=("metric", "value"))


def run_test(frame, test_name, value_column, group_column=""):
    """Run a supported test and return a table suitable for the Data Lab result view."""
    values = _numeric(frame, value_column)
    if test_name == "One-sample t-test":
        statistic, p_value = stats.ttest_1samp(values, 0)
        standard_error = stats.sem(values)
        interval = stats.t.interval(0.95, len(values) - 1, loc=values.mean(), scale=standard_error)
        return _result(test_name, "H0: the population mean equals 0", statistic, p_value,
                       "Independent numeric observations; approximate normality.", interval)
    if test_name == "Normality (Shapiro-Wilk)":
        if len(values) > 5000:
            values = values.sample(5000, random_state=42)
        statistic, p_value = stats.shapiro(values)
        return _result(test_name, "H0: the sample comes from a normal distribution", statistic, p_value,
                       "Sensitive to sample size; use a histogram or Q-Q plot too.")
    if test_name == "Correlation significance":
        if not group_column or group_column not in frame.columns:
            raise ValueError("Choose a second numeric column")
        other = pd.to_numeric(frame[group_column], errors="coerce")
        paired = pd.concat([values.rename("x"), other.rename("y")], axis=1).dropna()
        if len(paired) < 3:
            raise ValueError("Correlation needs at least three paired observations")
        statistic, p_value = stats.pearsonr(paired["x"], paired["y"])
        return _result(test_name, "H0: the population Pearson correlation is 0", statistic, p_value,
                       "Linear relationship, paired observations, and no influential outliers.")
    if test_name == "Independent t-test":
        if not group_column or group_column not in frame.columns:
            raise ValueError("Choose a grouping column")
        groups = frame[[value_column, group_column]].copy()
        groups[value_column] = pd.to_numeric(groups[value_column], errors="coerce")
        groups = groups.dropna()
        labels = list(groups[group_column].unique())
        if len(labels) != 2:
            raise ValueError("Independent t-test needs exactly two groups")
        first = groups.loc[groups[group_column] == labels[0], value_column]
        second = groups.loc[groups[group_column] == labels[1], value_column]
        statistic, p_value = stats.ttest_ind(first, second, equal_var=False)
        return _result(test_name, f"H0: the means of {labels[0]} and {labels[1]} are equal", statistic, p_value,
                       "Independent observations; approximately normal groups; Welch test does not require equal variance.")
    raise ValueError(f"Unknown statistical test: {test_name}")
