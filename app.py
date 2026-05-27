import streamlit as st
import streamlit.components.v1 as components
from database.db import init_db
from components.auth import auth_page, logout, is_session_valid

# Force sidebar to start expanded
st.set_page_config(
    page_title="Infera Study AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    init_db()

    # Load and inject animated background component
    with open('components/background.html', 'r') as f:
        bg_html = f.read()

    st.markdown("""
<style>
/* Make the component iframe fixed as background */
iframe {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    z-index: -1 !important;
    border: none !important;
    pointer-events: none !important;
}
/* Make app transparent so background shows through */
html, body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMainViewContainer"],
[data-testid="stApp"],
.main,
[data-testid="stHeader"] {
    background: transparent !important;
    background-color: transparent !important;
}
</style>
""", unsafe_allow_html=True)

    components.html(bg_html, height=1, scrolling=False)

    # Global CSS injection featuring Animated Subtle Grain Overlay and Glowing Orbs
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Instrument+Serif:ital@0;1&display=swap');

        /* Base styling over transparent background */
        html, body, .stApp {
            font-family: 'Inter', sans-serif !important;
            color: #FFFFFF !important;
        }
        html, body,
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMainViewContainer"],
        [data-testid="stApp"] {
            background: transparent !important;
            background-color: transparent !important;
        }

        /* Page fade-in animation */
        .block-container {
            animation: pageIn 0.3s ease forwards;
            padding: 32px 40px !important;
            max-width: 1100px !important;
        }
        @keyframes pageIn {
            from { opacity: 0; transform: translateY(6px); }
            to   { opacity: 1; transform: translateY(0); }
        }

        /* ── Cards — frosted glass over colorful bg ── */
        .glass-card,
        [data-testid="stMetric"],
        [data-testid="stDataFrame"],
        [data-testid="stForm"],
        .stExpander,
        .kpi-card {
            background: rgba(10, 8, 20, 0.55) !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            backdrop-filter: blur(24px) !important;
            -webkit-backdrop-filter: blur(24px) !important;
            border-radius: 12px !important;
        }
        [data-testid="stForm"] {
            padding: 24px !important;
        }
        [data-testid="stForm"] > div {
            background: transparent !important;
        }
        .glass-card {
            padding: 20px !important;
            transition: border-color 0.2s ease !important;
        }
        .glass-card:hover {
            border-color: rgba(255,255,255,0.15) !important;
        }

        /* ── Sidebar — frosted dark glass ── */
        [data-testid="stSidebar"] {
            background: rgba(8, 6, 18, 0.75) !important;
            border-right: 1px solid rgba(255,255,255,0.08) !important;
            backdrop-filter: blur(30px) !important;
            -webkit-backdrop-filter: blur(30px) !important;
        }

        /* Force sidebar toggle button to always show */
        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapsedControl"] {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            pointer-events: all !important;
            z-index: 99999 !important;
            position: fixed !important;
            top: 16px !important;
            left: 16px !important;
            background: rgba(13,15,20,0.9) !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            border-radius: 8px !important;
            padding: 6px !important;
            backdrop-filter: blur(10px) !important;
            cursor: pointer !important;
        }
        [data-testid="collapsedControl"]:hover,
        [data-testid="stSidebarCollapsedControl"]:hover {
            background: rgba(255,255,255,0.08) !important;
            border-color: rgba(255,255,255,0.2) !important;
        }
        [data-testid="collapsedControl"] svg,
        [data-testid="stSidebarCollapsedControl"] svg {
            fill: rgba(255,255,255,0.6) !important;
            color: rgba(255,255,255,0.6) !important;
            width: 18px !important;
            height: 18px !important;
        }

        /* Nav button hover glow effect */
        [data-testid="stSidebar"] .stButton button {
            position: relative !important;
            overflow: hidden !important;
            transition: all 0.2s ease !important;
        }
        [data-testid="stSidebar"] .stButton button::before {
            content: '' !important;
            position: absolute !important;
            left: 0 !important; top: 0 !important; bottom: 0 !important;
            width: 2px !important;
            background: rgba(255,255,255,0) !important;
            transition: background 0.2s ease !important;
            border-radius: 0 !important;
        }
        [data-testid="stSidebar"] .stButton button:hover::before {
            background: rgba(255,255,255,0.4) !important;
        }
        [data-testid="stSidebar"] .stButton button:hover {
            background: rgba(255,255,255,0.06) !important;
            color: #FFFFFF !important;
            padding-left: 18px !important;
        }

        /* Hide default Streamlit sidebar navigation links */
        [data-testid="stSidebarNav"] {
            display: none !important;
        }

        /* ── Hide Streamlit chrome ── */
        footer { visibility: hidden !important; }
        .stDeployButton { display: none !important; }

        /* ── Scrollbar ── */
        ::-webkit-scrollbar { width: 3px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { 
            background: rgba(255,255,255,0.08); 
            border-radius: 99px; 
        }

        /* ── Input fields — glass style ── */
        div[data-baseweb="input"],
        div[data-baseweb="textarea"],
        div[data-baseweb="select"] {
            background: rgba(255,255,255,0.06) !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            border-radius: 8px !important;
            transition: border-color 0.2s ease !important;
        }
        .stTextInput input, .stTextArea textarea,
        .stSelectbox select, .stNumberInput input {
            background: transparent !important;
            border: none !important;
            color: #FFFFFF !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 13px !important;
        }
        div[data-baseweb="input"]:focus-within, 
        div[data-baseweb="textarea"]:focus-within {
            border-color: rgba(180, 140, 200, 0.5) !important;
            box-shadow: 0 0 0 3px rgba(150, 100, 180, 0.15) !important;
            outline: none !important;
        }
        div[data-testid="stNumberInput"] button {
            background: rgba(255,255,255,0.05) !important;
            border: none !important;
            color: #FFFFFF !important;
            transition: background 0.2s ease !important;
        }
        div[data-testid="stNumberInput"] button:hover {
            background: rgba(255,255,255,0.15) !important;
        }
        .stTextInput label, .stTextArea label,
        .stSelectbox label, .stNumberInput label {
            color: rgba(255,255,255,0.35) !important;
            font-size: 10px !important;
            font-weight: 500 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.08em !important;
        }

        /* ── Buttons ── */
        .stButton button {
            background: rgba(255,255,255,0.08) !important;
            border: 1px solid rgba(255,255,255,0.14) !important;
            color: #FFFFFF !important;
            backdrop-filter: blur(10px) !important;
            border-radius: 8px !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
            letter-spacing: 0.01em !important;
        }
        .stButton button:hover {
            background: rgba(255,255,255,0.15) !important;
            border-color: rgba(255,255,255,0.28) !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 20px rgba(0,0,0,0.4) !important;
        }

        /* ── Primary button ── */
        .btn-primary {
            background: #FFFFFF !important;
            color: #000000 !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }
        .btn-primary:hover {
            background: rgba(255,255,255,0.9) !important;
        }

        /* ── Metrics ── */
        [data-testid="stMetric"]:hover {
            border-color: rgba(255,255,255,0.22) !important;
            background: rgba(10, 8, 20, 0.65) !important;
        }
        [data-testid="stMetricValue"] {
            font-family: 'Instrument Serif', serif !important;
            font-style: italic !important;
            font-size: 2.2rem !important;
            color: #FFFFFF !important;
            letter-spacing: -1px !important;
            text-shadow: 0 2px 10px rgba(0,0,0,0.4) !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 10px !important;
            text-transform: uppercase !important;
            letter-spacing: 0.1em !important;
            color: rgba(255,255,255,0.45) !important;
            font-weight: 500 !important;
        }

        /* ── Dataframe over colorful bg ── */
        [data-testid="stDataFrame"],
        div.stDataFrameGlideDataEditor,
        .stDataFrame,
        [data-testid="stDataFrameResizable"] {
            background: rgba(10, 8, 20, 0.55) !important;
            background-color: rgba(10, 8, 20, 0.55) !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            border-radius: 12px !important;
            backdrop-filter: blur(24px) !important;
            -webkit-backdrop-filter: blur(24px) !important;

            /* Glide Data Grid theming custom variables */
            --gdg-bg-cell: rgba(10, 8, 20, 0.55) !important;
            --gdg-bg-cell-medium: rgba(14, 11, 26, 0.6) !important;
            --gdg-bg-header: rgba(21, 19, 37, 0.75) !important;
            --gdg-bg-header-hover: rgba(30, 27, 52, 0.8) !important;
            --gdg-text-dark: #ffffff !important;
            --gdg-text-medium: rgba(255, 255, 255, 0.85) !important;
            --gdg-text-light: rgba(255, 255, 255, 0.6) !important;
            --gdg-border-color: rgba(255, 255, 255, 0.1) !important;
            --gdg-accent-color: rgba(150, 100, 200, 0.3) !important;
            --gdg-accent-light: rgba(150, 100, 200, 0.15) !important;
        }
        [data-testid="stDataFrame"] [data-testid="stDataFrameResizable"] {
            background: transparent !important;
            background-color: transparent !important;
        }
        [data-testid="stDataFrame"] canvas {
            background: transparent !important;
            background-color: transparent !important;
        }

        /* ── Slider track over colorful bg ── */
        .stSlider [data-baseweb="slider"] [role="progressbar"] {
            background: rgba(180, 140, 220, 0.7) !important;
        }
        .stSlider [data-baseweb="slider"] [role="slider"] {
            background: #FFFFFF !important;
            box-shadow: 0 2px 12px rgba(150, 100, 200, 0.6) !important;
        }

        /* ── Auth page card ── */
        .auth-card {
            background: rgba(8, 6, 18, 0.7) !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            backdrop-filter: blur(30px) !important;
        }

        /* ── Tab styling over colorful bg ── */
        .stTabs [data-baseweb="tab-list"] {
            background: rgba(255,255,255,0.05) !important;
            backdrop-filter: blur(10px) !important;
        }

        /* ── Altair charts ── */
        .vega-embed, canvas { background: transparent !important; }
        [data-testid="stVegaLiteChart"] {
            background: rgba(8, 6, 18, 0.65) !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            border-radius: 12px !important;
            padding: 16px !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
        }

        /* ── Headings ── */
        h1, h2, h3, .section-title {
            font-family: 'Instrument Serif', serif !important;
            font-style: italic !important;
            color: #FFFFFF !important;
            text-shadow: 0 2px 20px rgba(0,0,0,0.5) !important;
        }
        h4, h5, h6 {
            font-family: 'Instrument Serif', serif !important;
            font-style: italic !important;
            color: #FFFFFF !important;
            letter-spacing: -0.5px !important;
        }
        p, span, label, div {
            color: rgba(255,255,255,0.85) !important;
        }

        /* ── KPI metric cards ── */
        .kpi-card {
            padding: 18px 20px !important;
            position: relative !important;
            overflow: hidden !important;
        }
        .kpi-card::before {
            content: '' !important;
            position: absolute !important;
            top: 0 !important; left: 0 !important; right: 0 !important;
            height: 1px !important;
            background: linear-gradient(90deg, 
                transparent, 
                rgba(255,255,255,0.15), 
                transparent) !important;
        }
        .kpi-value {
            font-family: 'Instrument Serif', serif !important;
            font-style: italic !important;
            font-size: 2.2rem !important;
            color: #FFFFFF !important;
            line-height: 1 !important;
            letter-spacing: -1px !important;
        }
        .kpi-label {
            font-size: 11px !important;
            color: rgba(255,255,255,0.4) !important;
            text-transform: uppercase !important;
            letter-spacing: 0.08em !important;
            margin-top: 6px !important;
            font-weight: 500 !important;
        }
        .kpi-delta {
            font-size: 11px !important;
            color: rgba(255,255,255,0.3) !important;
            margin-top: 4px !important;
        }

        /* ── Section headings ── */
        .section-title {
            font-size: 1.8rem !important;
            line-height: 1.1 !important;
        }
        .section-sub {
            font-size: 12px !important;
            color: rgba(255,255,255,0.35) !important;
            font-weight: 400 !important;
            margin-top: 4px !important;
            letter-spacing: 0.02em !important;
        }

        /* ── Dividers ── */
        .subtle-divider {
            height: 1px !important;
            background: rgba(255,255,255,0.06) !important;
            margin: 16px 0 !important;
        }

        /* ── Table styling ── */
        .data-table {
            width: 100% !important;
            border-collapse: collapse !important;
            font-size: 13px !important;
        }
        .data-table th {
            text-align: left !important;
            padding: 8px 12px !important;
            color: rgba(255,255,255,0.3) !important;
            font-size: 10px !important;
            text-transform: uppercase !important;
            letter-spacing: 0.1em !important;
            font-weight: 500 !important;
            border-bottom: 1px solid rgba(255,255,255,0.06) !important;
        }
        .data-table td {
            padding: 10px 12px !important;
            color: rgba(255,255,255,0.8) !important;
            border-bottom: 1px solid rgba(255,255,255,0.04) !important;
            vertical-align: middle !important;
        }
        .data-table tr:hover td {
            background: rgba(255,255,255,0.02) !important;
        }

        /* ── Progress bar ── */
        .progress-track {
            background: rgba(255,255,255,0.07) !important;
            border-radius: 99px !important;
            height: 4px !important;
            width: 100% !important;
            overflow: hidden !important;
        }
        .progress-fill {
            height: 100% !important;
            border-radius: 99px !important;
            transition: width 0.3s ease !important;
        }

        /* ── Chat bubbles ── */
        .msg-user {
            display: flex !important;
            justify-content: flex-end !important;
            margin: 6px 0 !important;
        }
        .msg-user-inner {
            background: rgba(255,255,255,0.08) !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            border-radius: 12px 12px 2px 12px !important;
            padding: 10px 14px !important;
            max-width: 62% !important;
            font-size: 13px !important;
            line-height: 1.55 !important;
            color: #FFFFFF !important;
        }
        .msg-ai {
            display: flex !important;
            justify-content: flex-start !important;
            margin: 6px 0 !important;
        }
        .msg-ai-inner {
            background: rgba(255,255,255,0.03) !important;
            border: 1px solid rgba(255,255,255,0.07) !important;
            border-radius: 2px 12px 12px 12px !important;
            padding: 10px 14px !important;
            max-width: 62% !important;
            font-size: 13px !important;
            line-height: 1.55 !important;
            color: rgba(255,255,255,0.85) !important;
        }

        /* ── Token stats badge ── */
        .token-badge {
            display: inline-flex !important;
            align-items: center !important;
            gap: 12px !important;
            background: rgba(255,255,255,0.03) !important;
            border: 1px solid rgba(255,255,255,0.07) !important;
            border-radius: 99px !important;
            padding: 5px 14px !important;
            font-size: 11px !important;
            color: rgba(255,255,255,0.35) !important;
            font-family: 'Inter', sans-serif !important;
            margin-top: 8px !important;
        }
        .token-badge span {
            color: rgba(255,255,255,0.6) !important;
            font-weight: 500 !important;
        }

        /* ── Mobile responsiveness & load fix ── */
        @media (max-width: 768px) {
            .block-container {
                padding: 16px !important;
            }
            [data-testid="stSidebar"] {
                width: 260px !important;
            }
        }

        /* Ensure no white flash on load */
        html, body {
            background: transparent !important;
            background-color: transparent !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Check if user is logged in
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        pg = st.navigation([st.Page(auth_page, title="Login / Register")])
    else:
        # Check session validity
        if not is_session_valid():
            pg = st.navigation([st.Page(auth_page, title="Login / Register")])
        else:
            pages_list = [
                st.Page("pages/dashboard.py", title="Dashboard"),
                st.Page("pages/planner.py", title="Planner"),
                st.Page("pages/tasks.py", title="Task Manager"),
                st.Page("pages/infera_flow.py", title="Infera Flow"),
                st.Page("pages/analytics.py", title="Analytics"),
                st.Page("pages/chat.py", title="AI Assistant"),
                st.Page("pages/profile.py", title="Profile"),
            ]
            pg = st.navigation(pages_list, position="sidebar")

            # Route mapping to resolve st.switch_page paths
            page_paths = {
                "Dashboard": "pages/dashboard.py",
                "Planner": "pages/planner.py",
                "Task Manager": "pages/tasks.py",
                "Infera Flow": "pages/infera_flow.py",
                "Analytics": "pages/analytics.py",
                "AI Assistant": "pages/chat.py",
                "Profile": "pages/profile.py"
            }

            # Map the currently selected streamlit page returned by st.navigation to keep state in sync
            title_to_key = {
                "Dashboard": "Dashboard",
                "Planner": "Planner",
                "Task Manager": "Task Manager",
                "Infera Flow": "Infera Flow",
                "Analytics": "Analytics",
                "AI Assistant": "AI Assistant",
                "Profile": "Profile"
            }
            st.session_state['current_page'] = title_to_key.get(pg.title, "Dashboard")

            with st.sidebar:
                # Logo block
                st.markdown("""
                <div style="padding:24px 20px 20px; border-bottom:1px solid rgba(255,255,255,0.06);">
                    <div style="font-family:'Instrument Serif',serif; font-style:italic; 
                    font-size:1.3rem; color:#FFFFFF; letter-spacing:-0.3px;">Infera</div>
                    <div style="font-size:9px; color:rgba(255,255,255,0.2); margin-top:2px; 
                    text-transform:uppercase; letter-spacing:0.15em;">Study AI</div>
                </div>
                <div style="padding:16px 12px 8px; font-size:9px; color:rgba(255,255,255,0.2); 
                text-transform:uppercase; letter-spacing:0.12em;">Navigation</div>
                """, unsafe_allow_html=True)

                pages = ["Dashboard", "Planner", "Task Manager", 
                         "Infera Flow", "Analytics", "AI Assistant"]
                
                for page in pages:
                    is_active = st.session_state.get('current_page') == page
                    
                    # Style active vs inactive with CSS injection per button
                    if is_active:
                        st.markdown(f"""
                        <style>
                        div[data-testid="stButton"]:has(button[key="{page}_nav"]) button {{
                            background: rgba(255,255,255,0.08) !important;
                            color: #FFFFFF !important;
                            border: 1px solid rgba(255,255,255,0.12) !important;
                            text-align: left !important;
                            font-weight: 500 !important;
                            border-radius: 8px !important;
                            padding: 9px 14px !important;
                            width: 100% !important;
                            font-size: 13px !important;
                            margin: 1px 0 !important;
                        }}
                        </style>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <style>
                        div[data-testid="stButton"]:has(button[key="{page}_nav"]) button {{
                            background: transparent !important;
                            color: rgba(255,255,255,0.45) !important;
                            border: 1px solid transparent !important;
                            text-align: left !important;
                            font-weight: 400 !important;
                            border-radius: 8px !important;
                            padding: 9px 14px !important;
                            width: 100% !important;
                            font-size: 13px !important;
                            margin: 1px 0 !important;
                        }}
                        </style>
                        """, unsafe_allow_html=True)
                    
                    if st.button(page, key=f"{page}_nav", use_container_width=True):
                        st.session_state['current_page'] = page
                        st.switch_page(page_paths[page])

                # Spacer to push bottom section down
                st.markdown("""
                <div style="flex:1; min-height:40px;"></div>
                """, unsafe_allow_html=True)

                # Bottom user section - fixed at bottom
                st.markdown("""
                <style>
                .user-bottom-block {
                    position: fixed;
                    bottom: 0;
                    left: 0;
                    width: 288px;
                    padding: 14px 16px;
                    background: #0D0F14;
                    border-top: 1px solid rgba(255,255,255,0.06);
                }
                .user-bottom-block .logged-label {
                    font-size: 9px;
                    color: rgba(255,255,255,0.2);
                    text-transform: uppercase;
                    letter-spacing: 0.1em;
                    margin-bottom: 4px;
                }
                .user-bottom-block .user-name {
                    font-size: 13px;
                    font-weight: 500;
                    color: #FFFFFF;
                    margin-bottom: 10px;
                }
                </style>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="user-bottom-block">
                    <div class="logged-label">Logged in as</div>
                    <div class="user-name">{st.session_state.get('name', 'User')}</div>
                </div>
                """, unsafe_allow_html=True)

                # Profile and Logout buttons pinned at bottom
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("""
                    <style>
                    div[data-testid="stButton"]:has(button[key="profile_nav"]) button {
                        background: rgba(255,255,255,0.05) !important;
                        border: 1px solid rgba(255,255,255,0.08) !important;
                        color: rgba(255,255,255,0.6) !important;
                        font-size: 11px !important;
                        padding: 6px 10px !important;
                        border-radius: 6px !important;
                        width: 100% !important;
                        position: fixed;
                        bottom: 16px;
                        left: 16px;
                        width: 120px !important;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    if st.button("Profile", key="profile_nav"):
                        st.session_state['current_page'] = 'Profile'
                        st.switch_page(page_paths['Profile'])
                with col2:
                    st.markdown("""
                    <style>
                    div[data-testid="stButton"]:has(button[key="logout_nav"]) button {
                        background: rgba(255,255,255,0.05) !important;
                        border: 1px solid rgba(255,255,255,0.08) !important;
                        color: rgba(255,255,255,0.6) !important;
                        font-size: 11px !important;
                        padding: 6px 10px !important;
                        border-radius: 6px !important;
                        position: fixed;
                        bottom: 16px;
                        left: 148px;
                        width: 120px !important;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    if st.button("Logout", key="logout_nav"):
                        for key in list(st.session_state.keys()):
                            del st.session_state[key]
                        st.rerun()

    pg.run()

if __name__ == "__main__":
    main()
