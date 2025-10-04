import streamlit as st
import base64
import os

# ==================================
# 🌐 Page Config
# ==================================
st.set_page_config(
    page_title="ClariData - The AI Data Analyst",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================================
# 🖼️ Load Logo
# ==================================
LOGO_PATH = os.path.join("assets", "claridata_logo.png")
logo_base64 = ""
if os.path.exists(LOGO_PATH):
    with open(LOGO_PATH, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode("utf-8")

# ==================================
# 💅 Custom CSS (Sticky Navbar + Responsive)
# ==================================
st.markdown(f"""
    <style>
        /* Hide Streamlit default UI */
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

        /* ---------- FIXED NAVBAR ---------- */
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

        /* Left Section */
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
            letter-spacing: -0.5px;
        }}

        /* Right Section */
        .nav-right {{
            display: flex;
            gap: 1rem;
            align-items: center;
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

        /* ---------- HERO SECTION ---------- */
        .hero {{
            height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding-top: 8rem;
            background: linear-gradient(180deg, #ffffff 0%, #f9fafb 100%);
        }}
        .logo {{
            width: 140px;
            height: auto;
            margin-bottom: 1rem;
        }}
        .hero h1 {{
            font-size: 3rem;
            font-weight: 800;
            color: #0b132b;
            margin-bottom: 1rem;
        }}
        .hero p {{
            font-size: 1.2rem;
            color: #374151;
            margin-bottom: 3rem;
            max-width: 600px;
        }}
        .cta-btn {{
            background-color: #2563eb;
            color: white !important;
            padding: 0.9rem 2.2rem;
            border-radius: 8px;
            font-weight: 600;
            font-size: 1rem;
            text-decoration: none;
            transition: background-color 0.3s ease;
        }}
        .cta-btn:hover {{
            background-color: #1d4ed8;
        }}

        /* ---------- FOOTER ---------- */
        footer {{
            margin-top: 3rem;
            padding: 2rem 0;
            font-size: 0.9rem;
            color: #6b7280;
            text-align: center;
            border-top: 1px solid #e5e7eb;
            background-color: #fafafa;
        }}

        /* ---------- RESPONSIVE ---------- */
        @media (max-width: 768px) {{
            .navbar {{
                flex-direction: column;
                height: auto;
                padding: 1rem 2rem;
                gap: 0.5rem;
            }}
            .hero {{
                padding-top: 10rem;
            }}
            .hero h1 {{
                font-size: 2.2rem;
            }}
            .hero p {{
                font-size: 1rem;
                padding: 0 1rem;
            }}
        }}
    </style>
""", unsafe_allow_html=True)

# ==================================
# 🧭 Navbar (Static)
# ==================================
nav_logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="nav-logo" alt="ClariData Logo">' if logo_base64 else '<span class="nav-title">ClariData</span>'

st.markdown(f"""
<div class="navbar">
    <div class="nav-left">
        {nav_logo_html}
        <span class="nav-title">ClariData</span>
    </div>
    <div class="nav-right">
    <a href="/Data_Analyzer" target="_self" class="nav-btn">🧠 Analyzer</a>
    <a href="/Dashboard" target="_self" class="nav-btn">📈 Dashboard</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ==================================
# 🧠 Hero Section
# ==================================
hero_logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="logo" alt="ClariData Logo">' if logo_base64 else ''

st.markdown(f"""
<div class="hero">
    {hero_logo_html}
    <h1>The AI Data Analyst</h1>
    <p>Connect your data, ask questions in plain English,<br>
    and get insights in seconds. No coding required.</p>
    <a href="/1_Data_Analyzer" target="_self" class="cta-btn">
        🚀 Try ClariData Free
    </a>
</div>
""", unsafe_allow_html=True)

# ==================================
# 👣 Footer
# ==================================
st.markdown("""
<footer>
    © 2025 <strong>ClariData</strong> — AI-Powered Business Insights
</footer>
""", unsafe_allow_html=True)
