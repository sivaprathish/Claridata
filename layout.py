# layout.py
import streamlit as st
import base64
import os

def load_logo_base64():
    LOGO_PATH = os.path.join("assets", "claridata_logo.png")
    if os.path.exists(LOGO_PATH):
        with open(LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

def render_shared_layout(page_title="ClariData"):
    logo_base64 = load_logo_base64()

    st.set_page_config(
        page_title=page_title,
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # --- Custom CSS ---
    st.markdown(f"""
    <style>
        [data-testid="stSidebar"], header {{
            display: none !important;
        }}
        .block-container {{
            padding: 0 !important;
            margin: 0 !important;
        }}
        body {{
            background-color: #ffffff;
            font-family: 'Inter', sans-serif;
        }}

        .navbar {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 70px;
            background-color: #ffffff;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 4rem;
            z-index: 1000;
        }}

        .nav-left {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .nav-logo {{
            height: 42px;
            width: auto;
        }}
        .nav-title {{
            font-size: 1.4rem;
            font-weight: 700;
            color: #1e3a8a;
        }}
        .nav-right {{
            display: flex;
            gap: 1rem;
        }}
        .nav-btn {{
            background-color: #2563eb;
            color: white !important;
            padding: 0.6rem 1.4rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.95rem;
            transition: background-color 0.3s ease;
        }}
        .nav-btn:hover {{
            background-color: #1d4ed8;
        }}
        footer {{
            margin-top: 4rem;
            padding: 2rem 0;
            font-size: 0.9rem;
            color: #6b7280;
            text-align: center;
            border-top: 1px solid #e5e7eb;
            background-color: #fafafa;
        }}
    </style>
    """, unsafe_allow_html=True)

    # --- Navbar ---
    nav_logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="nav-logo" alt="ClariData Logo">'
    st.markdown(f"""
    <div class="navbar">
        <div class="nav-left">
            {nav_logo_html}
            <span class="nav-title">ClariData</span>
        </div>
        <div class="nav-right">
            <a href="/Data_Analyzer" target="_self" class="nav-btn">🚀 Analyzer</a>
            <a href="/Dashboard" target="_self" class="nav-btn">📈 Dashboard</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_footer():
    st.markdown("""
    <footer>
        © 2025 <strong>ClariData</strong> — AI-Powered Business Insights
    </footer>
    """, unsafe_allow_html=True)
