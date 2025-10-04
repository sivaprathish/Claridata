import polars as pl
import json
import os


def analyze_dataset(file_path: str):
    """
    Analyze a dataset (CSV, Excel, or JSON) using Polars
    and return structured metadata.
    """

    # ------------------------------
    # 1. Detect file type & load dataset
    # ------------------------------
    ext = os.path.splitext(file_path)[1].lower()

    if ext in [".csv"]:
        df = pl.read_csv(file_path)

    elif ext in [".xlsx", ".xls"]:
        # Excel is not natively supported by Polars, so read via pandas bridge
        import pandas as pd
        df = pl.from_pandas(pd.read_excel(file_path))

    elif ext in [".json"]:
        # For JSON files, read as a Polars DataFrame
        try:
            df = pl.read_json(file_path)
        except Exception:
            # fallback if JSON is list-of-dicts or nested
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

    # ------------------------------
    # 3. Summary statistics
    # ------------------------------
    summary_df = df.describe()

    # Convert Polars describe() to dict-of-dicts
    summary_named = {}
    for i, stat_name in enumerate(summary_df["statistic"].to_list()):
        for col in summary_df.columns:
            if col == "statistic":
                continue
            summary_named.setdefault(col, {})[stat_name] = summary_df[col][i]

    # ------------------------------
    # 4. Add datetime summaries if applicable
    # ------------------------------
    for col in df.columns:
        dtype = df[col].dtype
        if dtype in (pl.Datetime, pl.Date):
            col_min = df[col].min()
            col_max = df[col].max()
            col_range = col_max - col_min
            summary_named[col] = {
                "min": str(col_min),
                "max": str(col_max),
                "range": str(col_range)
            }

    # ------------------------------
    # 5. Correlations (numeric only)
    # ------------------------------
    numeric_cols = [
        col for col, dtype in dtypes.items()
        if any(t in dtype for t in ("Int", "Float"))
    ]

    correlations = {}
    for col1 in numeric_cols:
        correlations[col1] = {}
        for col2 in numeric_cols:
            try:
                corr_val = df.select(pl.corr(pl.col(col1), pl.col(col2))).item()
                correlations[col1][col2] = corr_val
            except Exception:
                correlations[col1][col2] = None

    # ------------------------------
    # 6. Build metadata package
    # ------------------------------
    metadata = {
        "columns": columns,
        "data_types": dtypes,
        "missing_values": missing,
        "summary_statistics": summary_named,
        "correlations": correlations,
    }

    return metadata


# ------------------------------
# 7. Standalone testing
# ------------------------------
if __name__ == "__main__":
    file_path = "Housing.csv"  # or "data.xlsx", "data.json"
    result = analyze_dataset(file_path)
    
