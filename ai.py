import json
import os
from typing import Union
import google.generativeai as genai

# Lazy import pandas only if needed. We don't want pandas as a hard dependency
try:
    import pandas as pd
except Exception:
    pd = None

# Import the analyzer so callers can pass a file path to generate metadata
try:
    from data_analysis import analyze_dataset
except Exception:
    analyze_dataset = None


def generate_ai_insights(metadata: Union[dict, str], api_key: str = None):
    """
    Use Google Gemini to generate business-friendly insights,
    KPIs, and visualization suggestions from dataset metadata.
    """
    # =============================
    # 1. Configure Gemini
    # =============================

    # Try environment variable first, fallback to provided or default key
    api_key = ("AIzaSyAsCQ4fAGS6NtIXXMiQdmDaUH6yqvpFIHU" 
    )

    if not api_key:
        raise ValueError(
            "❌ Gemini API key not found. Please set GEMINI_API_KEY or pass it directly."
        )

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-pro")

    # If caller passed a file path string or PathLike, try to use
    # data_analysis.analyze_dataset to build a metadata dict.
    if isinstance(metadata, (str, os.PathLike)):
        if analyze_dataset is not None:
            # If a file path was provided, analyze it to produce metadata
            try:
                metadata = analyze_dataset(str(metadata))
            except Exception as e:
                raise RuntimeError(f"Failed to analyze dataset at {metadata}: {e}")
        else:
            raise RuntimeError(
                "analyze_dataset from data_analysis.py is not available."
            )

    # If metadata is a pandas DataFrame (e.g., passed directly from Streamlit upload),
    # convert it to a lightweight serializable summary so json.dumps doesn't fail.
    def _make_json_serializable(obj):
        # Convert non-JSON-serializable objects (especially pandas DataFrames)
        # into lightweight, JSON-safe structures before embedding into prompts.
        #
        # Why: json.dumps cannot serialize DataFrame objects. Streamlit commonly
        # passes a pandas.DataFrame from a file upload; embedding that directly
        # into the model prompt caused the TypeError you saw. We convert the
        # DataFrame into a concise summary (schema + up to 10 sample rows) so
        # the prompt remains readable and small while preserving useful info.
        #
        # If you need a different representation (full CSV, larger sample, or
        # column statistics), update this helper accordingly.

        # DataFrame -> to_dict(orient="records") for small previews, or a summary dict
        if pd is not None and isinstance(obj, pd.DataFrame):
            # Convert a small sample plus schema info to keep the prompt concise
            try:
                return {
                    "type": "dataframe",
                    "num_rows": int(obj.shape[0]),
                    "num_columns": int(obj.shape[1]),
                    "columns": [
                        {
                            "name": str(c),
                            "dtype": str(obj[c].dtype)
                        }
                        for c in obj.columns
                    ],
                    "sample_rows": obj.head(10).to_dict(orient="records")
                }
            except Exception:
                # Fallback: convert to records (may be large)
                try:
                    return obj.head(10).to_dict(orient="records")
                except Exception:
                    return str(obj)

        # If it's a dict containing DataFrames, convert them recursively
        if isinstance(obj, dict):
            new = {}
            for k, v in obj.items():
                new[k] = _make_json_serializable(v)
            return new

        # For lists/tuples, process items
        if isinstance(obj, (list, tuple)):
            return [_make_json_serializable(x) for x in obj]

        # Default: return as-is (json.dumps will raise if truly non-serializable)
        return obj

    metadata = _make_json_serializable(metadata)

   


    # =============================
    # 2. Build Prompt (Strict JSON Output)
    # =============================
    prompt = f"""
You are a business data analyst.

Here is metadata of a dataset:
{json.dumps(metadata, indent=2)}

Your task: Return the output STRICTLY in JSON format with no extra text, markdown, or code block.

The JSON must have this structure:

{{
  "dataset_summary": {{
    "title": "short dataset name (plain English, easy for anyone to understand)",
    "description": "short simple summary of what the dataset is about",
    "size": <number of records>,
    "key_columns": ["list of important columns in plain words"]
  }},
  "kpis": [
    {{
      "title": "short friendly label for dashboard card (non-technical, easy for anyone)",
      "insight": "plain-English finding, no jargon",
      "trend": "a supporting fact, count, or relationship phrased naturally (e.g., 'Out of 1,000 sales, 351 were electronics')",
      "value": "<main KPI value, rounded and human-readable like '4.7M', '351', or a category name>'",
      "unit": "human-friendly label like 'Dollars', 'Percent', 'Customers', or leave blank for categories",
      "change": "growth/decline phrased simply, e.g. '+5% higher than last year' (optional)"
    }}
  ],
  "visualizations": [
    {{
      "chart_type": "bar | pie | line | doughnut",
      "x": "<categorical column>",
      "y": "<numeric column or Count>",
      "x_label": "<clear descriptive label for x-axis>",
      "y_label": "<clear descriptive label for y-axis>",
      "title": "<short, clear chart title>",
      "insight": "<plain-English explanation of what the chart shows>"
    }}
  ]
}}

Rules:
- Do NOT include Issues or Suggestions.
- Do NOT wrap the output in triple backticks or markdown code blocks.
- Always provide numbers in 'value' when possible (use rounded shorthand for large numbers, e.g., '4.7M', '2.3K').
- Keep all text clear, simple, and non-technical.
- Include important visualization that best represents the dataset.
- Use readable units in standard form (e.g., "Square Feet", "Years", "Percent", "Dollars").
- Round large numbers and currencies for readability (e.g., 4.7M Dollars, 2.3K Items, 89%).
- Use only meaningful, intuitive visualizations that are easy for normal (non-technical) people to understand.
- Avoid overly complex or uncommon charts unless they add clear value.
- Keep all titles, labels, and insights concise, clear, and professional.
    """

    # =============================
    # 3. Send to Gemini & Get Response
    # =============================
    response = model.generate_content(prompt)

    # =============================
    # 4. Parse JSON Output
    # =============================
    raw = response.text if hasattr(response, "text") else str(response)

    clean = raw.strip()
    clean = clean.replace("```json", "```")
    if clean.startswith("```") and clean.endswith("```"):
        clean = clean[3:-3].strip()
    if clean.lower().startswith("json\n"):
        clean = clean[len("json\n"):].strip()

    insights_json = None
    try:
        insights_json = json.loads(clean)
        return insights_json
    except Exception as outer_e:
        import re

        m = re.search(r"(\{[\s\S]*\})", clean)
        if m:
            candidate = m.group(1)
            try:
                insights_json = json.loads(candidate)
                return insights_json
            except Exception as inner_e:
                print("⚠️ Could not parse extracted JSON candidate:", inner_e)

        print("⚠️ Could not parse JSON response:", outer_e)
        print("Raw output:", raw)
        return {"error": "Invalid JSON returned from Gemini", "raw_text": raw}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Quick demo: analyze a dataset and optionally generate AI insights using Gemini.")
    parser.add_argument("file", help="Path to dataset file (CSV, XLSX, JSON)")
    parser.add_argument("--api_key", help="Gemini API key (optional)")
    args = parser.parse_args()

    if analyze_dataset is None:
        print("data_analysis.analyze_dataset is not importable. Make sure data_analysis.py is in the same package or PYTHONPATH.")
        raise SystemExit(1)

    print(f"Analyzing: {args.file}")
    meta = analyze_dataset(args.file)
    print("--- Metadata summary ---")
    print(json.dumps({
        "dataset_overview": meta.get("dataset_overview"),
        "num_columns": len(meta.get("columns", [])),
        "top_correlations": meta.get("top_correlations", [])
    }, indent=2))

    # If user provided an API key, attempt to call Gemini; otherwise skip.
    if args.api_key:
        print("Calling Gemini to generate insights (this will use provided API key)...")
        out = generate_ai_insights(meta, api_key=args.api_key)
        print("--- AI Insights ---")
        print(json.dumps(out, indent=2))
    else:
        print("No API key provided; skipping call to Gemini. Provide --api_key to call the model.")
