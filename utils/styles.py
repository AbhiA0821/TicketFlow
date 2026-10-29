"""
UI Design System and CSS tokens for TicketFlow.
Black & Yellow SaaS Theme.
"""

BLACK_YELLOW_CSS = """
<style>
/* Root font and layout */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: #F5F5F5;
}

/* Background overrides */
.stApp {
    background-color: #0B0B0B;
}

[data-testid="stSidebar"] {
    background-color: #111111;
    border-right: 1px solid #262626;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1rem;
}

/* Main content header spacing */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

/* Headings */
h1, h2, h3, h4 {
    color: #F5F5F5 !important;
    font-weight: 600;
    letter-spacing: -0.02em;
}

p, span, label {
    color: #A3A3A3;
}

/* Streamlit Native Button Overrides */
div.stButton > button:first-child {
    background-color: #FACC15;
    color: #0B0B0B;
    font-weight: 600;
    border: none;
    border-radius: 8px;
    padding: 0.55rem 1.25rem;
    transition: all 0.2s ease-in-out;
}

div.stButton > button:first-child:hover {
    background-color: #FDE047;
    color: #0B0B0B;
    box-shadow: 0 4px 14px rgba(250, 204, 21, 0.3);
    transform: translateY(-1px);
}

div.stButton > button:first-child:active {
    transform: translateY(0);
}

/* Secondary / Standard button styling */
div[data-testid="stButton"] > button[kind="secondary"] {
    background-color: #171717;
    color: #F5F5F5;
    border: 1px solid #303030;
}
div[data-testid="stButton"] > button[kind="secondary"]:hover {
    border-color: #FACC15;
    color: #FACC15;
    background-color: #202020;
}

/* Download button */
div.stDownloadButton > button {
    background-color: #171717 !important;
    color: #FACC15 !important;
    border: 1px solid #FACC15 !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    transition: all 0.2s ease-in-out !important;
}
div.stDownloadButton > button:hover {
    background-color: #FACC15 !important;
    color: #0B0B0B !important;
}

/* Text area & inputs */
textarea, input, [data-baseweb="input"], [data-baseweb="textarea"] {
    background-color: #171717 !important;
    color: #F5F5F5 !important;
    border: 1px solid #303030 !important;
    border-radius: 8px !important;
}

textarea:focus, input:focus, [data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within {
    border-color: #FACC15 !important;
    box-shadow: 0 0 0 1px #FACC15 !important;
}

/* Selectbox dropdowns */
div[data-baseweb="select"] > div {
    background-color: #171717 !important;
    border: 1px solid #303030 !important;
    color: #F5F5F5 !important;
    border-radius: 8px !important;
}

/* Metrics Cards override */
[data-testid="stMetric"] {
    background-color: #171717;
    border: 1px solid #303030;
    padding: 1.1rem 1.25rem;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
}
[data-testid="stMetricLabel"] {
    color: #A3A3A3 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
[data-testid="stMetricValue"] {
    color: #F5F5F5 !important;
    font-weight: 700 !important;
}

/* Streamlit dataframes */
[data-testid="stDataFrame"] {
    border: 1px solid #303030;
    border-radius: 8px;
    overflow: hidden;
}

/* Custom SaaS cards */
.tf-card {
    background-color: #171717;
    border: 1px solid #303030;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.25rem;
    transition: border-color 0.2s ease;
}
.tf-card:hover {
    border-color: #404040;
}
.tf-card-accent {
    border-left: 4px solid #FACC15;
}

/* Badges */
.tf-badge {
    display: inline-block;
    padding: 0.25rem 0.65rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.tf-badge-high {
    background-color: rgba(239, 68, 68, 0.15);
    color: #EF4444;
    border: 1px solid rgba(239, 68, 68, 0.35);
}
.tf-badge-medium {
    background-color: rgba(250, 204, 21, 0.15);
    color: #FACC15;
    border: 1px solid rgba(250, 204, 21, 0.35);
}
.tf-badge-low {
    background-color: rgba(34, 197, 94, 0.15);
    color: #22C55E;
    border: 1px solid rgba(34, 197, 94, 0.35);
}
.tf-badge-dept {
    background-color: #202020;
    color: #F5F5F5;
    border: 1px solid #383838;
}

/* Sidebar navigation item */
.tf-nav-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.65rem 1rem;
    margin: 0.2rem 0;
    border-radius: 8px;
    color: #A3A3A3;
    font-weight: 500;
    font-size: 0.95rem;
    text-decoration: none;
    transition: all 0.15s ease;
}
.tf-nav-item:hover {
    background-color: #1c1c1c;
    color: #F5F5F5;
}
.tf-nav-item.active {
    background-color: #202020;
    color: #FACC15;
    border-left: 3px solid #FACC15;
    font-weight: 600;
}

/* User profile card in sidebar */
.tf-profile-card {
    background-color: #171717;
    border: 1px solid #282828;
    border-radius: 10px;
    padding: 0.85rem;
    margin-top: 1.5rem;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: #0B0B0B;
}
::-webkit-scrollbar-thumb {
    background: #2a2a2a;
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: #FACC15;
}

/* Prevent alerts from blinding the theme */
.stAlert {
    background-color: #171717 !important;
    border: 1px solid #303030 !important;
    color: #F5F5F5 !important;
    border-radius: 8px !important;
}
</style>
"""


def apply_custom_styles():
    """Injects the Black and Yellow SaaS design system into the Streamlit session."""
    import streamlit as st
    st.markdown(BLACK_YELLOW_CSS, unsafe_allow_html=True)
