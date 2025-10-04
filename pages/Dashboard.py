import streamlit as st
import tempfile
import os
import pandas as pd
import json
import re
import plotly.express as px
from ai import generate_ai_insights
from layout import render_shared_layout, render_footer

# ---------- Visual styling constants ----------
COLOR_MAP = {
    "bar": ["#4F46E5", "#636EFA", "#00CC96", "#FFA15A", "#FF636E"],
    "line": ["#EF553B", "#4F46E5", "#00CC96"],
    "scatter": ["#00CC96", "#FFA15A", "#636EFA"],
    "pie": ["#19D3F3", "#FF6692", "#B6E880", "#FF97FF", "#FECB52"],
    "doughnut": ["#19D3F3", "#FF6692", "#B6E880", "#FF97FF", "#FECB52"]
}

# ===================================
# Shared Layout (navbar + global CSS)
# ===================================
render_shared_layout("ClariData Dashboard")

st.markdown("<div style='margin-top:100px'></div>", unsafe_allow_html=True)
st.title("📊 AI Dashboard Generator")

# ===================================
# Upload Section
# ===================================
uploaded_file = st.file_uploader("📂 Upload your dataset", type=["csv", "xlsx", "xls", "json"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    st.success(f"✅ File `{uploaded_file.name}` uploaded successfully!")

    # Load data
    ext = uploaded_file.name.split('.')[-1].lower()
    df = None
    try:
        if ext == "csv":
            df = pd.read_csv(tmp_path)
        elif ext in ["xlsx", "xls"]:
            df = pd.read_excel(tmp_path)
        elif ext == "json":
            df = pd.read_json(tmp_path)
    except Exception as e:
        st.error(f"❌ Could not read file: {e}")

    if df is not None:
        st.dataframe(df.head())

        # ===================================
        # AI Insights
        # ===================================
        st.info("🤖 Generating AI insights... please wait ⏳")
        ai_output = generate_ai_insights(df)

        raw_output = ai_output.get("raw_text", json.dumps(ai_output))
        clean_json = re.sub(r"^```[a-zA-Z]*|```$", "", raw_output.strip()).strip()
        clean_json = re.sub(r"^json\s*", "", clean_json).strip()

        try:
            parsed = json.loads(clean_json)
        except Exception as e:
            st.error(f"⚠️ Failed to parse AI output: {e}")
            st.stop()

        summary = parsed.get("dataset_summary", {})
        kpis = parsed.get("kpis", [])
        viz_recs = parsed.get("visualizations", [])

        # ===================================
        # Inject Dashboard CSS (copied from Dash)
        # ===================================
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
            font-weight: 700;
            font-size: 20px;
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
        </style>
        """, unsafe_allow_html=True)

        # ===================================
        # Dashboard Layout
        # ===================================
        st.markdown("<div class='dashboard-wrapper'>", unsafe_allow_html=True)

        # Header Summary
        st.markdown(f"""
        <div style='text-align:center; margin-bottom:40px'>
            <h2 style='color:#1E3A8A; font-weight:700;'>{summary.get("title", "Dashboard")}</h2>
            <p style='color:#4B5563; max-width:800px; margin:0 auto;'>
                {summary.get("description", "")}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # =======================
        # KPI Cards
        # =======================
        if kpis:
            st.markdown("<h3 class='section-title'>📈 Key Performance Indicators</h3>", unsafe_allow_html=True)
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

        # =======================
        # Visualization Cards
        # =======================
        if viz_recs:
            st.markdown("<h3 class='section-title'>📊 Visual Insights</h3>", unsafe_allow_html=True)
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
                        template="plotly_white",
                        hovermode="closest",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        margin=dict(l=24, r=24, t=48, b=24),
                    )

                    # Slight marker/enhancement for bars/lines
                    try:
                        if hasattr(fig, "update_traces"):
                            fig.update_traces(marker=dict(opacity=0.92, line=dict(width=0.5, color="#ffffff")))
                    except Exception:
                        pass

                    st.markdown("<div class='card-hover'>", unsafe_allow_html=True)
                    st.plotly_chart(fig, use_container_width=True)
                    if insight:
                        st.markdown(f"<p class='chart-insight'>💡 {insight}</p>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("👆 Upload a file to generate your dashboard.")

# ===================================
# Footer (same as analyzer)
# ===================================
render_footer()
