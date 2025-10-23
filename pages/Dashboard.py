import streamlit as st
import os
import pandas as pd
import json
import re
import plotly.express as px
from ai import generate_ai_insights
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

/* Consistent headings */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', sans-serif !important;
    color: #1E3A8A !important;
    font-weight: 700 !important;
}

/* Buttons */
.stButton>button {
    background-color: #4F46E5 !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 24px !important;
    font-weight: 600 !important;
    font-size: 16px !important;
    transition: 0.3s ease;
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

/* Centering and consistent width for sections */
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
    box-shadow: 0;
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

/* KPI Cards */
.kpi-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    transition: 0.3s ease;
}
.kpi-card:hover {
    transform: scale(1.02);
}

/* Caption styling */
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
</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================
render_shared_layout("ClariData Dashboard")
st.markdown("<div style='margin-top:40px'></div>", unsafe_allow_html=True)

# ============================================================
# STEPPER SECTION
# ============================================================
st.markdown("""
<div style='text-align:center; margin-top:40px;'>
    <h5 class="main-heading">Upload your data and get instant insights</h5>
    <div class="stepper-container">
        <div class="step-item">
            <div class="step-circle">1</div>
            <div class="step-label">Choose a File</div>
        </div>
        <div class="step-item">
            <div class="step-circle">2</div>
            <div class="step-label">Convert in a Click</div>
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
# AI INSIGHTS
# ============================================================
if df is not None:
    # Create a placeholder for the "please wait" message
    placeholder = st.empty()
    placeholder.info("Generating AI insights... please wait")

    # Generate insights
    try:
        ai_output = generate_ai_insights(df)
    except Exception as e:
        placeholder.empty()  # Remove waiting message if failed
        st.error(f"❌ Error generating AI insights: {e}")
        st.stop()

    # Remove the "please wait" message after getting the result
    placeholder.empty()

    # Process AI output
    raw_output = ai_output.get("raw_text", json.dumps(ai_output))
    clean_json = re.sub(r"^[a-zA-Z]*|$", "", raw_output.strip()).strip()
    clean_json = re.sub(r"^json\\s*", "", clean_json).strip()

    try:
        parsed = json.loads(clean_json)
    except Exception as e:
        st.error(f"⚠ Failed to parse AI output: {e}")
        st.stop()

    summary = parsed.get("dataset_summary", {})
    kpis = parsed.get("kpis", [])
    viz_recs = parsed.get("visualizations", [])

    st.markdown("""
        <style>
        .dashboard-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 30px 40px;
            max-width: 1600px;
            margin: 0 auto;
        }
        .section {
            width: 100%;
            margin-bottom: 50px;
        }
        .section-title {
            color: #1E3A8A;
            font-weight: 500;
            font-size: 9px;
            margin: 15px 0 25px;
            border-left: 4px solid #1E3A8A;
            padding-left: 12px;
        }
        .grid-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            justify-content: center;
        }
        .card-hover {
            background: white;
            color: #333;
            padding: 20px;
            border-radius: 18px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.25s ease, box-shadow 0.25s ease;
        }
        .card-hover:hover {
            transform: translateY(-6px) scale(1.02);
            box-shadow: 0px 10px 25px rgba(0,0,0,0.15);
        }
        .kpi-title {
            color: #1E40AF;
            font-weight: 600;
            font-size: 16px;
            margin-bottom: 6px;
        }
        .kpi-value {
            color: #16A34A;
            font-weight: 700;
            font-size: 24px;
            margin-bottom: 6px;
        }
        .kpi-insight {
            font-size: 14px;
            color: #4B5563;
            line-height: 1.4;
            margin-bottom: 6px;
        }
        .kpi-trend {
            color: #9CA3AF;
            font-size: 13px;
        }
        .chart-insight {
            font-size: 13px;
            color: #4B5563;
            margin-top: 10px;
        }
        .card-hover {
            background: white;
            color: #333;
            padding: 20px;
            border-radius: 18px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.25s ease, box-shadow 0.25s ease;
        }
        .card-hover {
            margin-bottom: 30px;
        }
        </style>
        """, unsafe_allow_html=True)

        # ===================================
        # Dashboard Layout
        # ===================================
    st.markdown("<div class='dashboard-wrapper'>", unsafe_allow_html=True)

    # HEADER
    st.markdown(f"""
        <div style='text-align:center; margin-bottom:40px'>
            <h2 style='color:#1E3A8A; font-weight:700;'>{summary.get("title", "Dashboard")}</h2>
            <p style='color:#4B5563; max-width:800px; margin:0 auto;'>
                {summary.get("description", "")}
            </p>
        </div>
        """, unsafe_allow_html=True)

    # KPIs
    if kpis:
        st.markdown("<h4 class='section-title'> - Key Performance Indicators</h4>", unsafe_allow_html=True)
        st.markdown("<div class='grid-container'>", unsafe_allow_html=True)
        for k in kpis:
            change = f" ({k['change']})" if k.get("change") else ""
            st.markdown(f"""
                <div class='card-hover'>
                    <div class='kpi-title'>{k.get("title", "KPI")}</div>
                    <div class='kpi-value'>{k.get("value", "")} {k.get("unit", "")}</div>
                    <div class='kpi-insight'>{k.get("insight", "")}</div>
                    <div class='kpi-trend'>{(k.get("trend", "") or "") + change}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    # VISUALIZATIONS
    COLOR_MAP = {
        "bar": ["#4F46E5", "#636EFA", "#00CC96", "#FFA15A", "#FF636E"],
        "line": ["#EF553B", "#4F46E5", "#00CC96"],
        "scatter": ["#00CC96", "#FFA15A", "#636EFA"],
        "pie": ["#19D3F3", "#FF6692", "#B6E880", "#FF97FF", "#FECB52"],
        "doughnut": ["#19D3F3", "#FF6692", "#B6E880", "#FF97FF", "#FECB52"]
    }

    if viz_recs:
        st.markdown("<h4 class='section-title'> - Visual Insights</h4>", unsafe_allow_html=True)
        st.markdown("<div class='grid-container'>", unsafe_allow_html=True)

        for viz in viz_recs:
            chart_type = viz.get("chart_type")
            x = viz.get("x")
            y = viz.get("y")
            insight = viz.get("insight", "")
            title = viz.get("title", "Visualization")

            # normalize and safety checks for columns
            if x not in df.columns:
                continue

                # Treat 'Count' (or 'count') as a special indicator to use value counts
            y_is_count = isinstance(y, str) and y.strip().lower() == "count"

                # If y is provided but not a dataframe column and not 'count', skip this viz
            if y and not y_is_count and y not in df.columns:
                continue

            fig = None
            if chart_type == "scatter" and y and not y_is_count:
                fig = px.scatter(
                        df,
                        x=x,
                        y=y,
                        color_discrete_sequence=COLOR_MAP.get("scatter"),
                        hover_data={y: True},
                    )
            elif chart_type == "line" and y and not y_is_count:
                fig = px.line(
                        df,
                        x=x,
                        y=y,
                        color_discrete_sequence=COLOR_MAP.get("line"),
                    )
            elif chart_type == "bar":
                if y_is_count or not y:
                        # Use counts of x
                    count_df = df[x].value_counts().reset_index()
                    count_df.columns = [x, "count"]
                    fig = px.bar(
                            count_df,
                            x=x,
                            y="count",
                            color=x,
                            color_discrete_sequence=COLOR_MAP.get("bar"),
                        )
                else:
                        # y exists (checked above). If numeric, aggregate by mean; otherwise plot raw values
                    if pd.api.types.is_numeric_dtype(df[y]):
                        try:
                            avg_df = df.groupby(x)[y].mean().reset_index()
                            fig = px.bar(
                                    avg_df,
                                    x=x,
                                    y=y,
                                    color=x,
                                    color_discrete_sequence=COLOR_MAP.get("bar"),
                                )
                        except Exception:
                            fig = px.bar(
                                    df,
                                    x=x,
                                    y=y,
                                    color=x,
                                    color_discrete_sequence=COLOR_MAP.get("bar"),
                                )
                    else:
                        fig = px.bar(
                                df,
                                x=x,
                                y=y,
                                color=x,
                                color_discrete_sequence=COLOR_MAP.get("bar"),
                            )
            elif chart_type == "pie":
                fig = px.pie(df, names=x, color_discrete_sequence=COLOR_MAP.get("pie"))
            elif chart_type == "doughnut":
                fig = px.pie(
                        df,
                        names=x,
                        values=y if y and not y_is_count else None,
                        hole=0.4,
                        color_discrete_sequence=COLOR_MAP.get("doughnut"),
                    )

            if fig:
                    # Polished layout for each figure
                fig.update_layout(
                        title=dict(text=title, x=0.5, xanchor='center', font=dict(family="Inter, Segoe UI", size=18, color="#222")),
                        font=dict(family="Inter, Segoe UI", size=14, color="#333"),
                        template="plotly_white",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        plot_bgcolor='rgba(245,247,250,0.9)',
                        paper_bgcolor='rgba(245,247,250,0.9)',
                        margin=dict(l=24, r=24, t=48, b=24),
                    )

                    # Slight marker/enhancement for bars/lines
                try:
                    if hasattr(fig, "update_traces"):
                        fig.update_traces(marker=dict(opacity=0.92, line=dict(width=0.5, color="#ffffff")))
                except Exception:
                        pass

                # st.markdown("<div class='card-hover'>", unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                if insight:
                    st.markdown(f"<p class='chart-insight'>{insight}</p>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# FOOTER
# ============================================================
render_footer()