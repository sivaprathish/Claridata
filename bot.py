import json
import google.generativeai as genai
import polars as pl
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


# ===========================================
# 1. Configure Gemini
# ===========================================
# ⚠️ Replace this with your *own* valid API key.
genai.configure(api_key="AIzaSyAsCQ4fAGS6NtIXXMiQdmDaUH6yqvpFIHU")
model = genai.GenerativeModel("gemini-2.5-flash")

# ===========================================
# 2. Start a Chat Session
# ===========================================
chat = model.start_chat(
    history=[
        {
            "role": "user",
            "parts": [
                (
                    "You are a professional business data analyst. "
                    "You analyze dataset metadata and questions. "
                    "Always respond in valid JSON only — no markdown, code blocks, or extra text."
                )
            ],
        },
        {
            "role": "model",
            "parts": [
                "Understood. I will provide structured JSON answers only."
            ],
        },
    ]
)

# ===========================================
# 3. Helper Function: Extract JSON Safely
# ===========================================
def extract_json(text: str) -> dict:
    """
    Extract valid JSON from a Gemini text response.
    Handles markdown code fences and formatting.
    """
    text = text.strip()

    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if len(lines) > 2 else text
        text = text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from Gemini: {e}\nRaw text:\n{text}")

# ===========================================
# 4. Core Function: ask_data_question
# ===========================================
def ask_data_question(metadata: dict, question: str, df: pl.DataFrame, verbose: bool = False):
    """
    Analyze a question about data using Polars and Gemini.
    1. Checks if metadata alone can answer the question.
    2. If not, Gemini generates Polars code.
    3. Executes code safely and gets result.
    4. Sends result back for a final JSON answer.
    """
    # Step 1: Metadata sufficiency check
    check_prompt = f"""
Given this metadata:
{json.dumps(metadata, indent=2)}

And this question: "{question}"

Respond with JSON in this format:
{{
  "can_answer_from_metadata": true/false,
  "reason": "explanation",
  "answer": "answer if can_answer_from_metadata is true, otherwise null"
}}
"""
    response = chat.send_message(check_prompt)
    try:
        check_result = extract_json(response.text)
    except Exception:
        check_result = {
            "can_answer_from_metadata": False,
            "reason": "AI response invalid, proceeding with data analysis"
        }

    if check_result.get("can_answer_from_metadata"):
        return {
            "answer": check_result.get("answer"),
            "key_insights": ["Answer derived from metadata"],
            "suggested_visualization": None
        }

    # Step 2: Generate Polars code
    if verbose:
        print("⚙️ Generating Polars code...")

    try:
        sample_data = df.head(2).to_dicts()
    except Exception:
        sample_data = []

    code_prompt = f"""
Metadata insufficient to answer: "{question}"

Available DataFrame columns: {df.columns}
Shape: {df.shape}
Sample rows:
{json.dumps(sample_data, indent=2, default=str)}

Generate simple Polars code to answer the question.
Respond with JSON in this format:
{{
  "code": "polars code as string",
  "explanation": "what the code does"
}}

Rules:
- The DataFrame variable is 'df'.
- Final result variable must be 'analysis_result'.
- Use Polars syntax only.
- No imports or print statements.
- analysis_result must be JSON-serializable.
"""
    code_response = chat.send_message(code_prompt)

    try:
        code_result = extract_json(code_response.text)
        code_str = code_result["code"]
    except Exception:
        return {
            "answer": "Error: could not generate analysis code",
            "key_insights": ["Failed to parse AI response"],
            "suggested_visualization": None
        }

    if verbose:
        print("\nGenerated Polars code:\n", code_str)

    # Step 3: Execute generated code
    try:
        local_vars = {"df": df, "pl": pl}
        exec(code_str, {"pl": pl}, local_vars)
        analysis_result = local_vars.get("analysis_result")

        # Convert to JSON-serializable form
        if hasattr(analysis_result, "to_dict"):
            analysis_result = analysis_result.to_dict()
        elif hasattr(analysis_result, "to_dicts"):
            analysis_result = analysis_result.to_dicts()
        elif hasattr(analysis_result, "tolist"):
            analysis_result = analysis_result.tolist()
        elif hasattr(analysis_result, "item"):
            analysis_result = analysis_result.item()
    except Exception as e:
        return {
            "answer": f"Error executing AI-generated code: {e}",
            "key_insights": ["Code execution failed"],
            "suggested_visualization": None
        }

    # Step 4: Interpret result
    final_prompt = f"""
The question was: "{question}"

Polars code result:
{json.dumps(analysis_result, indent=2)}

Available columns: {df.columns}

Please answer the question in JSON format:
{{
  "answer": "your natural language answer",
  "key_insights": ["insight 1", "insight 2"],
  "suggested_visualization": {{
    "chart_type": "bar/line/pie/scatter/etc",
    "x_axis": "existing column name",
    "y_axis": "existing column name",
    "title": "descriptive chart title"
  }}
}}
"""
    final_response = chat.send_message(final_prompt)
    try:
        final_result = extract_json(final_response.text)
    except Exception:
        final_result = {"answer": final_response.text, "key_insights": [], "suggested_visualization": None}

    return {
        "answer": final_result.get("answer", "No answer generated"),
        "key_insights": final_result.get("key_insights", []),
        "suggested_visualization": final_result.get("suggested_visualization")
    }
