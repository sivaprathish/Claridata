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
# Force light mode globally
st.markdown("""
    <style>
    html, body, [class*="stAppViewContainer"], [class*="stApp"] {
        background-color: #ffffff !important;
        color-scheme: light !important;
    }
    </style>
""", unsafe_allow_html=True)


# ==================================
# 🖼 Load Logo
# ==================================

# Image paths
LOGO1_PATH = os.path.join("assets", "claridata_logo.png")
LOGO2_PATH = os.path.join("assets", "Data.png")
LOGO3_PATH = os.path.join("assets", "Automation.png")
LOGO4_PATH = os.path.join("assets", "Instant Insights.png")  

# Function to encode image to base64
def encode_image(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

# Encode each image
logo1_base64 = encode_image(LOGO1_PATH)
logo2_base64 = encode_image(LOGO2_PATH)
logo3_base64 = encode_image(LOGO3_PATH)
logo4_base64 = encode_image(LOGO4_PATH)

# ==================================
# 💅 Modern ClariData Style CSS
# ==================================
st.markdown(f"""
<style>
    [data-testid="stSidebar"], header {{
        display: none !important;
    }}
    .block-container {{
        padding: 0 !important;
        margin: 0 !important;
        overflow-x: hidden;
    }}
    body {{
        font-family: 'Inter', sans-serif;
        background: linear-gradient(180deg, #f9fafb 0%, #ffffff 100%);
        color: white;
    }}

    /* ---------- NAVBAR ---------- */
    .navbar {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 70px;
        background: rgba(255,255,255,0.85);
        backdrop-filter: blur(12px);
        border-bottom: 1px solid rgba(0,0,0,0.05);
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 3rem;
        z-index: 999;
    }}
    .nav-left {{
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    .nav-logo {{
        height: 42px;
    }}
    .nav-title {{
        font-size: 1.4rem;
        font-weight: 700;
        color: #1e3a8a;
    }}
    .nav-right {{
        display: flex;
        gap: 1.2rem;
    }}
    .nav-btn {{
        background: linear-gradient(90deg, #2563eb, #3b82f6);
        color: white !important;
        padding: 0.55rem 1.3rem;
        border-radius: 10px;
        font-weight: 600;
        text-decoration: none;
        transition: all 0.3s ease;
    }}
    .nav-btn:hover {{
        transform: scale(1.05);
        background: linear-gradient(90deg, #1e40af, #2563eb);
    }}

    /* ---------- HERO SECTION ---------- */
    .hero {{
        height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        background: radial-gradient(circle at 50% 10%, #e0f2fe 0%, #ffffff 70%);
        padding: 8rem 2rem 2rem 2rem;
    }}
    .hero-card {{
        background: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(15px);
        border-radius: 24px;
        padding: 3rem 4rem;
        box-shadow: none;
        max-width: 720px;
    }}
    .logo {{
        width: 120px;
        margin-bottom: 1rem;
    }}
    .hero h1 {{
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 1rem;
        color: #0f172a;
    }}
    .hero p {{
        font-size: 1.1rem;
        color: #475569;
        margin-bottom: 2.5rem;
    }}
    .cta-btn {{
        background: linear-gradient(90deg, #2563eb, #3b82f6);
        color: #fff !important;
        padding: 0.9rem 2.3rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1.05rem;
        text-decoration: none;
        transition: all 0.3s ease;
    }}
    .cta-btn:hover {{
        transform: translateY(-3px);
        background: linear-gradient(90deg, #1e40af, #2563eb);
    }}

/* ---------- FEATURES SECTION ---------- */
    .features {{
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 2rem;
        padding: 5rem 2rem;
        background-color: #ffffff;
    }}

    .feature-card {{
        background: #f9fafb;
        border-radius: 16px;
        padding: 2rem;
        width: 800px;
        height: 450px;
        display:flex;
        flex-direction:column;
        text-align: center;
        box-shadow: none;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
   }}

    /* .feature-card:hover {{
        transform: translateY(-6px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
    }} */

    .feature-icon {{
        font-size: 2rem;
        margin-bottom: 1rem;
    }}

    .feature-title {{
        font-weight: 800;
        font-size: 2.4rem;
        margin-bottom: 0.5rem;
        color: #0f172a;
    }}

    .feature-desc {{
        color: #475569;
        font-size: 1.1rem;
    }}

    /* Responsive */
    @media (max-width: 768px) {{
        .feature-card {{
            width: 90%;
        }}
    }}
    /* ---------- FOOTER ---------- */
    .footer {{
        text-align: center;
        font-size: 0.9rem;
        padding: 2rem;
        color: #6b7280;
        background: #fafafa;
        border-top: 1px solid #e5e7eb;
    }}

    @media (max-width: 768px) {{
        .navbar {{
            padding: 1rem 2rem;
            flex-direction: column;
            gap: 0.6rem;
        }}
        .hero-card {{
            padding: 2rem;
        }}
        .hero h1 {{
            font-size: 2.2rem;
        }}
    }}
</style>
""", unsafe_allow_html=True)

# ==================================
# 🧭 Navbar
# ==================================
nav_logo_html = (
    f'<img src="data:image/png;base64,{logo1_base64}" class="nav-logo" alt="ClariData Logo">'
    if logo1_base64
    else '<span class="nav-title">ClariData</span>'
)

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
# 🚀 Hero Section
# ==================================
hero_logo_html = (
    f'<img src="data:image/png;base64,{logo1_base64}" height="80" alt="ClariData Logo">'
    if logo1_base64
    else '<span class="nav-title">ClariData</span>'
)

st.markdown(f"""
<div style="
    text-align: center;
    padding: 6rem 2rem 2rem 2rem;
    font-family: 'Inter', sans-serif;
    background: radial-gradient(circle at 50% 10%, #e0f2fe 0%, #ffffff 70%);
">
    <div style="
        background: white;
        border-radius: 24px;
        box-shadow: none;
        display: inline-block;
        padding: 3rem 4rem;
        max-width: 700px;
    ">
        {hero_logo_html}
        <h1 style="
            font-size: 2.8rem;
            font-weight: 800;
            margin-bottom: 1rem;
            color: #0f172a;
        ">
            Meet <span style="color:#2563eb;">ClariData</span> — Your AI Data Analyst
        </h1>
        <p style="
            font-size: 1.1rem;
            color: #475569;
            margin-bottom: 2.5rem;
        ">
            Upload your data, ask questions in plain English, and let ClariData instantly generate insights,
            charts, and reports — no SQL or coding required.
        </p>
        <a href="/Data_Analyzer" target="_self" style="
            background: linear-gradient(90deg, #2563eb, #3b82f6);
            color: #fff;
            padding: 0.9rem 2.3rem;
            border-radius: 10px;
            font-weight: 600;
            font-size: 1.05rem;
            text-decoration: none;
            transition: all 0.3s ease;
        " onmouseover="this.style.transform='translateY(-3px)'"
          onmouseout="this.style.transform='translateY(0)'">
          🚀 Start Free Analysis
        </a>
    </div>
</div>
""", unsafe_allow_html=True)



# ==================================
# 🧩 Add Data, Ask Questions Section (Julius-style visual layout)
# ==================================

st.markdown(
    "<h2 style='text-align:center; font-size:2.4rem; font-weight:800; color:#0f172a;'>Add Data, Ask Questions</h2>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center; color:#475569; font-size:1.1rem; margin-top:-10px;'>Ask for what you want — ClariData will analyze it for you instantly.</p>",
    unsafe_allow_html=True,
)
st.markdown("")

# Create 3 columns for Step 1, 2, 3
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div style='text-align:center; background-color:#ffffff; border:1px solid #e5e7eb;
                    border-radius:20px; padding:30px 20px; box-shadow:none;'>
            <div style='background-color:#eff6ff; color:#2563eb; font-weight:700; display:inline-block;
                        border-radius:8px; padding:4px 10px; margin-bottom:10px;'>Step 1</div>
            <h3 style='font-size:1.3rem; color:#0f172a;'>Connect Your Data</h3>
            <p style='color:#475569; font-size:1rem;'>Import spreadsheets, databases, or cloud data sources in one click — ClariData automatically detects schema and cleans your data.</p>
            <img src="https://cdn-icons-png.flaticon.com/512/4175/4175852.png" width="80">
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div style='text-align:center; background-color:#ffffff; border:1px solid #e5e7eb;
                    border-radius:20px; padding:30px 20px; box-shadow:none;'>
            <div style='background-color:#eff6ff; color:#2563eb; font-weight:700; display:inline-block;
                        border-radius:8px; padding:4px 10px; margin-bottom:10px;'>Step 2</div>
            <h3 style='font-size:1.3rem; color:#0f172a;'>Ask Your Questions</h3>
            <p style='color:#475569; font-size:1rem;'>Type natural language prompts like “Show revenue trends by region” — no dashboards, just AI interpretation.</p>
            <img src="https://cdn-icons-png.flaticon.com/512/2554/2554827.png" width="80">
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div style='text-align:center; background-color:#ffffff; border:1px solid #e5e7eb;
                    border-radius:20px; padding:30px 20px; box-shadow:none;'>
            <div style='background-color:#eff6ff; color:#2563eb; font-weight:700; display:inline-block;
                        border-radius:8px; padding:4px 10px; margin-bottom:10px;'>Step 3</div>
            <h3 style='font-size:1.3rem; color:#0f172a;'>Get Insights Instantly</h3>
            <p style='color:#475569; font-size:1rem;'>Visualize results as charts, summaries, or reports. Export or share your analysis — all within seconds.</p>
            <img src="https://cdn-icons-png.flaticon.com/512/841/841364.png" width="80">
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("")
st.markdown(
    """
    <div style='text-align:center; margin-top:3rem;'>
        <a href="/Data_Analyzer" target="_self" style='background:linear-gradient(90deg,#2563eb,#3b82f6);
            color:#fff; padding:1rem 2.5rem; border-radius:12px; font-weight:600;
            text-decoration:none; font-size:1.1rem;'>✨ Try ClariData Now</a>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

data_html = (
    f'<img src="data:image/png;base64,{logo2_base64}" height="200" alt="ClariData Logo">'
    if logo2_base64
    else '<span class="nav-title">ClariData</span>'
)
automation_html = (
    f'<img src="data:image/png;base64,{logo3_base64}" height="200" alt="ClariData Logo">'
    if logo3_base64
    else '<span class="nav-title">ClariData</span>'
)
instant_html = (
    f'<img src="data:image/png;base64,{logo4_base64}" height="200" alt="ClariData Logo">'
    if logo4_base64
    else '<span class="nav-title">ClariData</span>'
)

# ✅ Make this an f-string!
st.markdown(f"""
<div class="features">

  <div class="feature-card">
      <div class="feature-icon">💬</div>
      <div class="feature-title">Chat with Your Data</div>
      <div class="feature-desc">
          Ask questions in plain English and get instant answers powered by AI.
      </div>
        <br>
        {data_html}
  </div>

  <div class="feature-card">
      <div class="feature-icon">📊</div>
      <div class="feature-title">Automatic Visuals</div>
      <div class="feature-desc">
          Get stunning charts and insights without writing a single line of code.
        </div>
      <br>
      {automation_html}
  </div>

  <div class="feature-card">
      <div class="feature-icon">⚡</div>
      <div class="feature-title">Instant Insights</div>
      <div class="feature-desc">
          Accelerate decisions with lightning-fast AI analysis on any dataset.
    </div>
      <br>
      {instant_html}
  </div>

</div>
""", unsafe_allow_html=True)




# ==================================
# 👣 Footer
# ==================================
st.markdown("""
<div class="footer">
    © 2025 <strong>ClariData</strong> — AI-Powered Business Insights
</div>
""", unsafe_allow_html=True)