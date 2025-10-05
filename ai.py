import json
import os
import time
import random
import google.generativeai as genai
import google.api_core.exceptions as google_exceptions


def generate_ai_insights(metadata: dict, api_key: str = None):
    """
    Use Google Gemini to generate business-friendly insights,
    KPIs, and visualization suggestions from dataset metadata.
    """

    # =============================
    # 1. Configure Gemini
    # =============================

    # Try environment variable first, fallback to provided key.
    # NOTE: removed any hard-coded API key to avoid accidental key exposure.
    api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError(
            "❌ Gemini API key not found. Please set GEMINI_API_KEY or pass it directly."
        )

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-pro")

    # If the caller passed a DataFrame (pandas or polars), convert it into a
    # JSON-serializable metadata dict so json.dumps won't fail.
    try:
        # Handle pandas DataFrame
        import pandas as _pd

        if isinstance(metadata, _pd.DataFrame):
            df = metadata
            metadata = {
                "columns": df.columns.tolist(),
                "data_types": {col: str(dtype) for col, dtype in zip(df.columns, df.dtypes)},
                "size": int(df.shape[0]) if df.shape is not None else len(df),
                "preview": df.head(10).to_dict(orient="records"),
            }
    except Exception:
        # pandas may not be installed or conversion failed; continue
        pass

    try:
        # Handle polars DataFrame (lazy import)
        import polars as _pl

        if isinstance(metadata, _pl.DataFrame):
            df = metadata
            cols = df.columns
            # polars types are not JSON serializable, so stringify them
            dtypes = {col: str(df[col].dtype) for col in cols}
            # preview: convert head to list of records
            preview_rows = []
            for row in df.head(10).rows():
                preview_rows.append(dict(zip(cols, row)))
            metadata = {
                "columns": cols,
                "data_types": dtypes,
                "size": int(df.height),
                "preview": preview_rows,
            }
    except Exception:
        pass

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
    # Attempt the request with a small exponential backoff retry loop to
    # handle transient quota/rate-limit errors (e.g., ResourceExhausted).
    max_attempts = 4
    base_delay = 1.0  # seconds
    response = None
    last_exception = None
    for attempt in range(1, max_attempts + 1):
        try:
            response = model.generate_content(prompt)
            last_exception = None
            break
        except google_exceptions.ResourceExhausted as e:
            # Likely quota/rate limit. Backoff and retry a few times then fail gracefully.
            last_exception = e
            if attempt == max_attempts:
                break
            # exponential backoff with jitter
            sleep_for = min(base_delay * (2 ** (attempt - 1)), 10) + random.random() * 0.5
            print(f"⚠️ ResourceExhausted on attempt {attempt}, backing off {sleep_for:.2f}s...")
            time.sleep(sleep_for)
            continue
        except Exception as e:
            # Non-retryable or unexpected error: capture and return a friendly dict
            print("⚠️ Unexpected error when calling Gemini:", e)
            return {"error": "request_failed", "message": str(e)}

    if last_exception is not None and response is None:
        # All retries exhausted. Provide a helpful error dict rather than raising.
        msg = (
            "The Gemini API returned ResourceExhausted (quota or rate limit). "
            "Please check your API quota, wait a moment, or reduce request frequency."
        )
        print("⚠️", msg, "Exception:", last_exception)
        return {"error": "ResourceExhausted", "message": msg, "details": str(last_exception)}

    # =============================
    # 4. Parse JSON Output
    # =============================
    # Clean the response to handle cases where the model wraps JSON in code fences
    raw = response.text if hasattr(response, "text") else str(response)

    # Remove common code fences and leading language hints (```json, ```)
    clean = raw.strip()
    # Remove triple backticks and optional language tag
    clean = clean.replace("```json", "```")
    if clean.startswith("```") and clean.endswith("```"):
        clean = clean[3:-3].strip()
    # Remove a leading 'json' token
    if clean.lower().startswith("json\n"):
        clean = clean[len("json\n"):].strip()

    # As a last resort, try to extract the first JSON object using a regex
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


# =============================
# 5. Optional: Standalone Test
# =============================
if __name__ == "__main__":
    from data_analysis import analyze_dataset

    # Example test with local file
    file_path = "Housing.csv"
    metadata = analyze_dataset(file_path)

    ai_output = generate_ai_insights(metadata)
