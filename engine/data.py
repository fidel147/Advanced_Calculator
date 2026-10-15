"""Data preparation helpers used by the Data Lab mode."""

from pathlib import Path
from html import escape

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


def read_table(path):
    """Read common local tabular formats with one validated entry point."""
    suffix = Path(path).suffix.lower()
    if suffix in (".xlsx", ".xls"):
        return pd.read_excel(path)
    if suffix == ".json":
        return pd.read_json(path)
    if suffix == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path, sep=None, engine="python")


def describe_table(frame, source_path=""):
    """Return compact, JSON-friendly metadata for a dataframe."""
    numeric = frame.select_dtypes(include="number")
    return {
        "file": Path(source_path).name,
        "rows": int(frame.shape[0]),
        "columns": int(frame.shape[1]),
        "missing": int(frame.isna().sum().sum()),
        "duplicates": int(frame.duplicated().sum()),
        "numeric_columns": list(numeric.columns),
        "column_types": {str(name): str(kind) for name, kind in frame.dtypes.items()},
        "profile": profile_table(frame),
    }


def dataset_summary(frame):
    """Return current dataset quality and memory metadata."""
    rows, columns = frame.shape
    missing = int(frame.isna().sum().sum())
    cells = max(rows * columns, 1)
    duplicate_percent = (frame.duplicated().sum() / max(rows, 1)) * 100
    quality_score = max(0.0, round(100 - (missing / cells * 100) - duplicate_percent, 2))
    return {
        "rows": int(rows),
        "columns": int(columns),
        "missing_values": missing,
        "missing_percent": round(missing / cells * 100, 2),
        "duplicate_rows": int(frame.duplicated().sum()),
        "data_quality_score": quality_score,
        "memory_bytes": int(frame.memory_usage(deep=True).sum()),
        "column_types": {str(name): str(dtype) for name, dtype in frame.dtypes.items()},
        "constant_columns": [str(name) for name in frame.columns if frame[name].nunique(dropna=False) <= 1],
    }


def descriptive_statistics(frame):
    """Compute numeric descriptive statistics with explicit sample semantics."""
    numeric = frame.select_dtypes(include="number")
    if numeric.empty:
        raise ValueError("The dataset has no numeric columns")
    rows = []
    for name in numeric.columns:
        values = numeric[name].dropna()
        if values.empty:
            continue
        quartiles = values.quantile([0.25, 0.5, 0.75])
        rows.append({
            "column": str(name), "count": int(values.size), "sum": float(values.sum()),
            "mean": float(values.mean()), "median": float(values.median()),
            "mode": float(values.mode().iloc[0]), "min": float(values.min()),
            "max": float(values.max()), "range": float(values.max() - values.min()),
            "variance_sample": float(values.var(ddof=1)) if len(values) > 1 else float("nan"),
            "std_sample": float(values.std(ddof=1)) if len(values) > 1 else float("nan"),
            "standard_error": float(values.sem()) if len(values) > 1 else float("nan"),
            "q1": float(quartiles.loc[0.25]), "q3": float(quartiles.loc[0.75]),
            "iqr": float(quartiles.loc[0.75] - quartiles.loc[0.25]),
            "skewness": float(values.skew()), "kurtosis_excess": float(values.kurt()),
        })
    return pd.DataFrame(rows)


def correlation_matrix(frame, method="pearson"):
    """Compute correlations only among numeric columns."""
    if method not in ("pearson", "spearman", "kendall"):
        raise ValueError("Correlation method must be pearson, spearman, or kendall")
    numeric = frame.select_dtypes(include="number")
    if numeric.shape[1] < 2:
        raise ValueError("Correlation needs at least two numeric columns")
    return numeric.corr(method=method)


def automated_eda(frame, source_path=""):
    """Build a deterministic EDA package from the current dataframe."""
    numeric = frame.select_dtypes(include="number")
    categorical = frame.select_dtypes(exclude="number")
    missing = frame.isna().sum().sort_values(ascending=False)
    report = {
        "summary": dataset_summary(frame) | {"file": Path(source_path).name},
        "missing": missing[missing > 0].rename_axis("column").reset_index(name="missing"),
        "numeric_statistics": descriptive_statistics(frame) if not numeric.empty else pd.DataFrame(),
        "correlations": correlation_matrix(frame) if numeric.shape[1] >= 2 else pd.DataFrame(),
        "categorical_frequencies": {
            str(column): frame[column].value_counts(dropna=False).head(10).rename_axis(str(column)).reset_index(name="count")
            for column in categorical.columns
        },
    }
    return report


def html_report(frame, source_path=""):
    """Render an offline HTML EDA report with escaped metadata and pandas tables."""
    report = automated_eda(frame, source_path)
    summary = report["summary"]
    cards = "".join(
        f"<div class='card'><b>{escape(str(key))}</b><br>{escape(str(value))}</div>"
        for key, value in summary.items()
        if key not in ("column_types", "constant_columns")
    )
    sections = ["<h2>Missing values</h2>", report["missing"].to_html(index=False, border=0)]
    if not report["numeric_statistics"].empty:
        sections.extend(["<h2>Numeric descriptive statistics</h2>",
                         report["numeric_statistics"].to_html(index=False, border=0)])
    if not report["correlations"].empty:
        sections.extend(["<h2>Pearson correlation</h2>", report["correlations"].to_html(border=0)])
    for column, values in report["categorical_frequencies"].items():
        sections.extend([f"<h2>Value counts: {escape(column)}</h2>", values.to_html(index=False, border=0)])
    return """<!doctype html><html><head><meta charset="utf-8"><title>Data Lab EDA</title>
<style>body{font-family:Arial,sans-serif;background:#202020;color:#eee;margin:32px}h1{color:#d8a84e}
.cards{display:flex;flex-wrap:wrap;gap:10px}.card{background:#383838;padding:12px;min-width:120px;border-radius:4px}
table{border-collapse:collapse;margin-bottom:24px;background:#383838}th,td{padding:7px 10px;border:1px solid #666}th{background:#555}</style></head>
<body><h1>Data Lab exploratory analysis</h1><div class="cards">""" + cards + "</div>" + "".join(sections) + "</body></html>"


def search_rows(frame, query):
    """Return rows containing a case-insensitive text match in any column."""
    query = str(query).strip()
    if not query:
        return frame.copy()
    mask = frame.astype(str).apply(lambda column: column.str.contains(query, case=False, na=False, regex=False)).any(axis=1)
    return frame.loc[mask].copy()


def profile_table(frame):
    """Return column-level quality and distribution information."""
    profile = {}
    for name in frame.columns:
        column = frame[name]
        numeric = pd.api.types.is_numeric_dtype(column)
        item = {
            "dtype": str(column.dtype),
            "missing": int(column.isna().sum()),
            "missing_percent": round(float(column.isna().mean() * 100), 2),
            "unique": int(column.nunique(dropna=True)),
        }
        if numeric:
            item.update({
                "mean": round(float(column.mean()), 6) if not column.dropna().empty else None,
                "std": round(float(column.std()), 6) if not column.dropna().empty else None,
                "min": float(column.min()) if not column.dropna().empty else None,
                "max": float(column.max()) if not column.dropna().empty else None,
            })
        profile[str(name)] = item
    return profile


def describe_frame(frame):
    """Return pandas describe output in a table-friendly form."""
    described = frame.describe(include="all").transpose().reset_index()
    return described.rename(columns={"index": "column"}).fillna("")


def value_counts(frame, column):
    """Return counts and percentages for one categorical or numeric column."""
    if column not in frame.columns:
        raise ValueError("Choose a value-count column")
    counts = frame[column].value_counts(dropna=False).rename_axis(column).reset_index(name="count")
    counts["percent"] = (counts["count"] / len(frame) * 100).round(2) if len(frame) else 0
    return counts


def group_summary(frame, group_column, value_column="", aggregation="count"):
    """Aggregate a value by groups for quick exploratory analysis."""
    if group_column not in frame.columns:
        raise ValueError("Choose a group column")
    if aggregation == "count":
        result = frame.groupby(group_column, dropna=False).size().reset_index(name="count")
    else:
        if value_column not in frame.columns:
            raise ValueError("Choose a numeric value column")
        if not pd.api.types.is_numeric_dtype(frame[value_column]):
            raise ValueError("Group aggregation needs a numeric value column")
        result = (frame.groupby(group_column, dropna=False)[value_column]
                  .agg(aggregation).reset_index(name=f"{aggregation}_{value_column}"))
    return result.sort_values(result.columns[-1], ascending=False).reset_index(drop=True)


def clean_table(frame, drop_missing=False, fill_numeric=False, drop_duplicates=False,
                fill_categorical=False, strip_text=False):
    """Apply selected, reproducible cleaning operations and return a new frame."""
    cleaned = frame.copy()
    if drop_duplicates:
        cleaned = cleaned.drop_duplicates()
    if fill_numeric:
        for column in cleaned.select_dtypes(include="number").columns:
            cleaned[column] = cleaned[column].fillna(cleaned[column].median())
    if fill_categorical:
        for column in cleaned.select_dtypes(exclude="number").columns:
            mode = cleaned[column].mode(dropna=True)
            if not mode.empty:
                cleaned[column] = cleaned[column].fillna(mode.iloc[0])
    if strip_text:
        for column in cleaned.select_dtypes(include="object").columns:
            cleaned[column] = cleaned[column].str.strip()
    if drop_missing:
        cleaned = cleaned.dropna()
    return cleaned.reset_index(drop=True)


def transform_table(frame, operation):
    """Apply a common data-science transformation and return a new dataframe."""
    transformed = frame.copy()
    if operation == "Normalize numeric":
        numeric = transformed.select_dtypes(include="number").columns
        for column in numeric:
            values = transformed[column]
            minimum, maximum = values.min(), values.max()
            if pd.notna(minimum) and maximum != minimum:
                transformed[column] = (values - minimum) / (maximum - minimum)
    elif operation == "Standardize numeric":
        numeric = transformed.select_dtypes(include="number").columns
        for column in numeric:
            values = transformed[column]
            mean, std = values.mean(), values.std()
            if pd.notna(std) and std != 0:
                transformed[column] = (values - mean) / std
    elif operation == "One-hot encode categories":
        transformed = pd.get_dummies(transformed, drop_first=False, dtype=float)
    elif operation == "Remove numeric outliers":
        numeric = transformed.select_dtypes(include="number")
        if numeric.empty:
            return transformed.reset_index(drop=True)
        first_quartile = numeric.quantile(0.25)
        third_quartile = numeric.quantile(0.75)
        spread = third_quartile - first_quartile
        low = first_quartile - 1.5 * spread
        high = third_quartile + 1.5 * spread
        mask = ~((numeric.lt(low)) | (numeric.gt(high))).any(axis=1)
        transformed = transformed.loc[mask]
    else:
        raise ValueError(f"Unknown transformation: {operation}")
    return transformed.reset_index(drop=True)


def train_baseline(frame, target, model_name="Random forest", test_size=0.2):
    """Train a small, explainable baseline and return metrics plus predictions."""
    if target not in frame.columns:
        raise ValueError("Choose a target column")
    usable = frame.dropna(subset=[target]).copy()
    features = usable.drop(columns=[target])
    features = pd.get_dummies(features, drop_first=False, dtype=float)
    features = features.replace([np.inf, -np.inf], np.nan)
    features = features.fillna(features.median(numeric_only=True)).fillna(0)
    if features.empty:
        raise ValueError("The dataset needs at least one feature column")
    target_values = usable[target]
    is_classification = model_name in ("Logistic regression", "Random forest classifier")
    encoder = None
    if is_classification:
        encoder = LabelEncoder()
        encoded_target = encoder.fit_transform(target_values.astype(str))
        if len(encoder.classes_) < 2:
            raise ValueError("Classification needs at least two target classes")
        if model_name == "Logistic regression":
            model = LogisticRegression(max_iter=1000)
        else:
            model = RandomForestClassifier(n_estimators=120, random_state=42)
        stratify = encoded_target if len(encoder.classes_) > 1 else None
        x_train, x_test, y_train, y_test = train_test_split(
            features, encoded_target, test_size=test_size, random_state=42, stratify=stratify)
        model.fit(x_train, y_train)
        predictions = model.predict(x_test)
        metrics = {
            "accuracy": round(float(accuracy_score(y_test, predictions)), 6),
            "f1_weighted": round(float(f1_score(y_test, predictions, average="weighted", zero_division=0)), 6),
        }
    else:
        numeric_target = pd.to_numeric(target_values, errors="coerce")
        valid = numeric_target.notna()
        features, numeric_target = features.loc[valid], numeric_target.loc[valid]
        if len(numeric_target) < 3:
            raise ValueError("Regression needs at least three numeric target values")
        if model_name == "Linear regression":
            model = LinearRegression()
        else:
            model = RandomForestRegressor(n_estimators=120, random_state=42)
        x_train, x_test, y_train, y_test = train_test_split(
            features, numeric_target, test_size=test_size, random_state=42)
        model.fit(x_train, y_train)
        predictions = model.predict(x_test)
        metrics = {
            "r2": round(float(r2_score(y_test, predictions)), 6),
            "rmse": round(float(np.sqrt(mean_squared_error(y_test, predictions))), 6),
            "mae": round(float(mean_absolute_error(y_test, predictions)), 6),
        }
    importance = getattr(model, "feature_importances_", None)
    if importance is None and hasattr(model, "coef_"):
        coefficients = np.abs(np.asarray(model.coef_))
        importance = coefficients.mean(axis=0) if coefficients.ndim > 1 else coefficients
    if importance is not None:
        metrics["feature_importance"] = dict(sorted(
            zip(features.columns, map(float, importance)), key=lambda item: item[1], reverse=True)[:10])
    return {"model": model, "metrics": metrics, "predictions": predictions, "encoder": encoder}