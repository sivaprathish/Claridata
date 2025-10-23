import streamlit as st
import os
import pandas as pd
import json
import plotly.express as px
import polars as pl
from bot import ask_data_question
from layout import render_shared_layout, render_footer

# ============================================================
# GLOBAL STYLE & FONT (Locks design consistency)
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="stAppViewContainer"], [class*="stApp"] {
    background-color: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
    color: #111827 !important;
    letter-spacing: 0.02em;
    color-scheme: light !important;
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', sans-serif !important;
    color: #1E3A8A !important;
    font-weight: 700 !important;
}

/* Centered large input box */
[data-testid="stTextInput"] {
    display: flex;
    justify-content: center;
    margin: 0 auto;
}
[data-testid="stTextInput"] input {
    
    font-size: 17px !important;
    text-align: center !important;
    border-radius: 12px !important;
    border: 1.5px solid #c8cae6 !important;
    padding: 10px 20px !important;
    box-shadow: 0 3px 8px rgba(0,0,0,0.05);
}

/* Centered smaller Ask button below input */
.stButton {
    display: flex;
    justify-content: center;
    margin-top: 20px;
}
.stButton>button {
    width: 100px !important;             /* Smaller than input */
    padding: 5px 0 !important;
    font-size: 17px !important;
    font-weight: 600 !important;
    background-color: #4F46E5 !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 10px rgba(79,70,229,0.25);
    transition: all 0.3s ease-in-out;
}
.stButton>button:hover {
    background-color: #3730A3 !important;
    transform: scale(1.03);
}

/* Tables */
.dataframe {
    border-radius: 10px !important;
    border: 1px solid #E5E7EB !important;
}
.dataframe td, .dataframe th {
    padding: 10px 12px !important;
}

/* Layout */
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1200px;
    margin: auto;
}

/* File uploader styling */
[data-testid="stFileUploader"] section div:first-child { display: none; }
[data-testid="stFileUploader"] {
    border: 2px dashed #4F46E5;
    border-radius: 18px;
    background-color: #F9FAFB;
    width: 640px;
    padding: 60px 0;
    text-align: center;
    margin: 0 auto;
    box-shadow: 0 10px 25px rgba(0,0,0,0.05);
    transition: 0.3s ease;
}
[data-testid="stFileUploader"]:hover {
    background-color: #EEF2FF;
    border-color: #3730A3;
    transform: scale(1.02);
}
[data-testid="stFileUploader"] label {
    color: #1E3A8A !important;
    font-size: 20px !important;
    font-weight: 700 !important;
}
[data-testid="stFileUploader"] small {
    color: #6B7280 !important;
    font-size: 14px !important;
}

/* Stepper */
.stepper-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #F9FAFB;
    padding: 30px 60px;
    border-radius: 16px;
    margin: 10px auto;
    width: 850px;
    max-width: 90%;
}
.step-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
    flex: 1;
}
.step-circle {
    background: #4F46E5;
    color: white;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    font-weight: 700;
    font-size: 18px;
    box-shadow: 0 4px 10px rgba(79,70,229,0.25);
}
.step-label {
    margin-top: 10px;
    font-weight: 600;
    color: #1E1E1E;
    text-align: center;
    font-size: 16px;
    white-space: nowrap;
}
.step-item:not(:last-child)::after {
    content: "";
    position: absolute;
    top: 25px;
    right: -50%;
    width: 100%;
    height: 3px;
    background-color: #E5E7EB;
    z-index: -1;
}
.main-heading {
    text-align: center;
    display: flex;
    justify-content: center;
    align-items: center;
    color: #1E3A8A;
    font-weight: 50;
    font-size: 10px;
    margin-bottom: 5px;
}

/* Caption */
caption, .stMarkdown p {
    color: #4B5563 !important;
}

/* Responsive */
@media (max-width: 768px) {
    .stepper-container {
        flex-direction: column;
        gap: 30px;
        padding: 20px;
    }
    .step-item:not(:last-child)::after {
        display: none;
    }
}

/* ChatBot Section Styling */
.chatbot-container {
    text-align: center;
    margin: 60px auto 20px;
    max-width: 700px;
}
.chatbot-container h2 {
    color: #1E3A8A;
    font-weight: 700;
    font-size: 28px;
    margin-bottom: 8px;
}
.chatbot-container p {
    color: #4B5563;
    font-size: 16px;
    margin-bottom: 25px;
}

/* Centered input styling */
[data-testid="stTextInput"] {
    text-align: center !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================
render_shared_layout("ClariData Analyzer")
st.markdown("<div style='margin-top:40px'></div>", unsafe_allow_html=True)

# ============================================================
# STEPPER SECTION
# ============================================================
st.markdown("""
<div style='text-align:center; margin-top:40px;'>
    <h5 class="main-heading">Upload your data and chat with AI for instant insights</h5>
    <div class="stepper-container">
        <div class="step-item">
            <div class="step-circle">1</div>
            <div class="step-label">Choose a File</div>
        </div>
        <div class="step-item">
            <div class="step-circle">2</div>
            <div class="step-label">Ask a Question</div>
        </div>
        <div class="step-item">
            <div class="step-circle">3</div>
            <div class="step-label">View Insights</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# FILE UPLOADER
# ============================================================
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    uploaded_file = st.file_uploader(" ", type=["csv", "xls", "xlsx"])

# ============================================================
# FILE HANDLER
# ============================================================
df = None
if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        st.success(f"✅ File {uploaded_file.name} uploaded successfully!")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"❌ Could not read file: {e}")
        df = None

# ============================================================
# CHATBOT INSIGHTS (Interactive)
# ============================================================
if df is not None:
    st.markdown("""
    <div class="chatbot-container">
        <h2>Ask the ChatBot about your data</h2>
        <p>Type your question below:</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        user_question = st.text_input("", placeholder="e.g. Which month had the highest sales?")
        ask_btn = st.button("Ask", use_container_width=True)

    if ask_btn:
        if not user_question.strip():
            st.warning("⚠ Please enter a question first.")
        else:
            placeholder = st.empty()
            placeholder.info("Chatbot is analyzing your data... please wait")

            try:
                metadata = {
                    "dataset_overview": {
                        "num_rows": int(df.shape[0]),
                        "num_columns": int(df.shape[1])
                    },
                    "columns": list(df.columns),
                    "data_types": {col: str(df[col].dtype) for col in df.columns},
                    "missing_values": {col: int(df[col].isna().sum()) for col in df.columns},
                    "sample_rows": df.head(10).to_dict(orient="records")
                }
            except Exception:
                metadata = {"columns": list(df.columns)}

            try:
                pl_df = pl.from_pandas(df)
            except Exception:
                try:
                    pl_df = pl.DataFrame(df.to_dict(orient="records"))
                except Exception:
                    st.error("❌ Failed to convert uploaded DataFrame to Polars DataFrame.")
                    st.stop()

            try:
                bot_output = ask_data_question(metadata, user_question, pl_df)
            except Exception as e:
                placeholder.empty()
                st.error(f"❌ Chatbot failed: {e}")
                st.stop()

            placeholder.empty()

            answer = bot_output.get("answer", "")
            key_insights = bot_output.get("key_insights", [])
            viz = bot_output.get("suggested_visualization", {})

            st.markdown(f"""
            <div style='text-align:center; margin:50px 0 30px;'>
                <h2>AI-Generated Insights</h2>
                <p style='color:#4B5563; font-size:18px; max-width:800px; margin:0 auto;'>
                    {answer}
                </p>
            </div>
            """, unsafe_allow_html=True)
            COLOR_MAP = {
                "bar": ["#4F46E5", "#636EFA", "#00CC96", "#FFA15A", "#FF636E"],
                "line": ["#EF553B", "#4F46E5", "#00CC96"],
                "scatter": ["#00CC96", "#FFA15A", "#636EFA"],
                "pie": ["#19D3F3", "#FF6692", "#B6E880", "#FF97FF", "#FECB52"],
                "doughnut": ["#19D3F3", "#FF6692", "#B6E880", "#FF97FF", "#FECB52"]
            }
            if key_insights:
                st.markdown("#### Key Insights")
                for insight in key_insights:
                    st.markdown(f"- {insight}")
            if viz:
                st.markdown("#### Suggested Visualization")
                chart_type = viz.get("chart_type", "").lower()
                x = viz.get("x_axis")
                y = viz.get("y_axis")
                title = viz.get("title", "Suggested Visualization")

                fig = None

                if x in df.columns:
                    if y in df.columns:
                        # 🔹 Automatically aggregate data to prevent duplicated bars
                        grouped_df = df.groupby(x, as_index=False)[y].sum()

                        if chart_type == "bar":
                            fig = px.bar(
                                grouped_df, x=x, y=y, title=title,
                                color=x, color_discrete_sequence=COLOR_MAP.get("bar")
                            )

                        elif chart_type == "line":
                            fig = px.line(
                                grouped_df, x=x, y=y, title=title,
                                color=x, color_discrete_sequence=COLOR_MAP.get("line")
                            )

                        elif chart_type == "scatter":
                            fig = px.scatter(
                                grouped_df, x=x, y=y, title=title,
                                color=x, color_discrete_sequence=COLOR_MAP.get("scatter")
                            )

                        elif chart_type == "pie":
                            fig = px.pie(
                                grouped_df, names=x, values=y, title=title,
                                color_discrete_sequence=COLOR_MAP.get("pie")
                            )

                    else:
                        # 🔹 Fallback for categorical-only plots (count plots)
                        count_df = df[x].value_counts().reset_index()
                        count_df.columns = [x, "count"]
                        fig = px.bar(
                            count_df, x=x, y="count", title=title,
                            color=x, color_discrete_sequence=COLOR_MAP.get("bar")
                        )

                if fig:
                    fig.update_layout(
                        template="plotly_white",
                        hovermode="closest",
                        bargap=0.3,
                        xaxis_title=x,
                        yaxis_title=y if y else "Count",
                        title_font=dict(size=17, color="black")
                    )
                    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# FOOTER
# ============================================================
render_footer()