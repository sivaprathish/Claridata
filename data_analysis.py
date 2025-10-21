import polars as pl
import json
import os
import numpy as np
import scipy.stats as stats


def analyze_dataset(file_path: str):
    """
    Comprehensive dataset analyzer supporting CSV, Excel, and JSON files.
    Generates metadata, summaries, correlations, and insights.
    """

    # ------------------------------
    # 1. Detect file type & load dataset
    # ------------------------------
    ext = os.path.splitext(file_path)[1].lower()

    if ext in [".csv"]:
        df = pl.read_csv(file_path)
    elif ext in [".xlsx", ".xls"]:
        import pandas as pd
        df = pl.from_pandas(pd.read_excel(file_path))
    elif ext in [".json"]:
        try:
            df = pl.read_json(file_path)
        except Exception:
            import pandas as pd
            df = pl.from_pandas(pd.read_json(file_path))
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    # ------------------------------
    # 2. Basic metadata
    # ------------------------------
    columns = df.columns
    dtypes = {col: str(df[col].dtype) for col in columns}
    missing = {col: int(df[col].null_count()) for col in columns}
    n_rows, n_cols = df.shape
    mem_usage_mb = round(sum(df[col].estimated_size() for col in df.columns) / 1_000_000, 3)

    # ------------------------------
    # 3. Summary statistics
    # ------------------------------
    summary_df = df.describe()
    summary_named = {}
    for i, stat_name in enumerate(summary_df["statistic"].to_list()):
        for col in summary_df.columns:
            if col == "statistic":
                continue
            summary_named.setdefault(col, {})[stat_name] = summary_df[col][i]

    # ------------------------------
    # 4. Column-level insights
    # ------------------------------
    column_insights = {}
    for col in columns:
        s = df[col]
        dtype = str(s.dtype)
        col_data = {"dtype": dtype, "missing": int(s.null_count())}

        # Unique values and mode
        try:
            col_data["unique_count"] = s.n_unique()
            mode_val = s.mode().to_list()
            col_data["mode"] = mode_val[0] if mode_val else None
        except Exception:
            col_data["unique_count"] = None
            col_data["mode"] = None

        # Top categories
        if "Utf8" in dtype or "Categorical" in dtype:
            try:
                freqs = s.value_counts().head(5).to_dict(as_series=False)
                col_data["top_values"] = dict(zip(freqs["column_0"], freqs["count"]))
            except Exception:
                col_data["top_values"] = None

        # Numeric stats & outliers
        if any(t in dtype for t in ("Int", "Float")):
            col_data["numeric_summary"] = {
                "mean": s.mean(),
                "std": s.std(),
                "min": s.min(),
                "max": s.max(),
                "q25": s.quantile(0.25),
                "median": s.median(),
                "q75": s.quantile(0.75),
                "skewness": s.skew(),
                "kurtosis": s.kurtosis()
            }
            q1, q3 = s.quantile(0.25), s.quantile(0.75)
            iqr = q3 - q1
            outliers = s.filter((s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr))
            col_data["outliers"] = outliers.height

        # Date range
        if s.dtype in (pl.Date, pl.Datetime):
            col_data["min"] = str(s.min())
            col_data["max"] = str(s.max())

        column_insights[col] = col_data

    # ------------------------------
    # 5. Correlations (numeric only)
    # ------------------------------
    numeric_cols = [
        col for col, dtype in dtypes.items()
        if any(t in dtype for t in ("Int", "Float"))
    ]

    correlations = {}
    top_corr_pairs = []
    for col1 in numeric_cols:
        correlations[col1] = {}
        for col2 in numeric_cols:
            try:
                corr_val = df.select(pl.corr(pl.col(col1), pl.col(col2))).item()
                correlations[col1][col2] = corr_val
                if col1 != col2 and corr_val is not None:
                    top_corr_pairs.append((col1, col2, abs(corr_val)))
            except Exception:
                correlations[col1][col2] = None

    top_corr_pairs_sorted = sorted(top_corr_pairs, key=lambda x: x[2], reverse=True)[:5]

    # ------------------------------
    # 6. Class imbalance (categoricals)
    # ------------------------------
    class_imbalance = {}
    for col in columns:
        if "Utf8" in str(df[col].dtype) or "Categorical" in str(df[col].dtype):
            value_counts = df[col].value_counts().to_dict(as_series=False)
            total = sum(value_counts["count"])
            class_imbalance[col] = {
                value_counts["column_0"][i]: {
                    "count": value_counts["count"][i],
                    "percentage": round(value_counts["count"][i] / total * 100, 2)
                }
                for i in range(len(value_counts["column_0"]))
            }

    # ------------------------------
    # 7. Duplicate rows
    # ------------------------------
    duplicates_count = df.height - df.unique(maintain_order=True).height

    # ------------------------------
    # 8. Entropy for categorical columns
    # ------------------------------
    entropy_values = {}
    for col in columns:
        s = df[col]
        if "Utf8" in str(s.dtype) or "Categorical" in str(s.dtype):
            total_count = len(s)
            probs = s.value_counts()["count"] / total_count
            entropy_values[col] = -float(np.sum(probs * np.log2(probs)))

    # ------------------------------
    # 9. Package metadata
    # ------------------------------
    metadata = {
        "dataset_overview": {
            "num_rows": n_rows,
            "num_columns": n_cols,
            "memory_usage_MB": mem_usage_mb
        },
        "columns": columns,
        "data_types": dtypes,
        "missing_values": missing,
        "summary_statistics": summary_named,
        "column_insights": column_insights,
        "correlations": correlations,
        "top_correlations": top_corr_pairs_sorted,
        "class_imbalance": class_imbalance,
        "duplicates_count": duplicates_count,
        "entropy_values": entropy_values,
    }

    return metadata
