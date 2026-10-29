"""
TicketFlow – NLP-Based Support Ticket Classification System
Modern SaaS Application with Black & Yellow Design System.
"""

import os
from datetime import datetime
import pandas as pd
import streamlit as st

# Local modules
from database.db import (
    authenticate_user,
    register_user,
    add_ticket,
    get_tickets,
    get_metrics,
    get_next_ticket_id,
)
from utils.ml_engine import (
    load_model_artifacts,
    classify_complaint,
    DEPARTMENT_MAPPING,
)
from utils.styles import apply_custom_styles

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="TicketFlow – AI Support Ticket Triage",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Black and Yellow SaaS Theme
apply_custom_styles()

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "authenticated_user" not in st.session_state:
    # Set default logged in user to demo account for smooth evaluation
    st.session_state.authenticated_user = {
        "email": "demo@ticketflow.io",
        "full_name": "Demo Admin"
    }

if "active_page" not in st.session_state:
    st.session_state.active_page = "Dashboard"

if "last_classified" not in st.session_state:
    st.session_state.last_classified = None

if "preset_text" not in st.session_state:
    st.session_state.preset_text = ""


# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------
def set_page(page_name: str):
    """Safely updates active page and triggers rerun."""
    st.session_state.active_page = page_name
    st.rerun()


def logout():
    """Clears authenticated session and navigates to Login."""
    st.session_state.authenticated_user = None
    st.session_state.active_page = "Login"
    st.rerun()


# ---------------------------------------------------------
# Verification: Model Artifacts Check
# ---------------------------------------------------------
model, vectorizer = load_model_artifacts()
if model is None or vectorizer is None:
    st.error("⚠️ Model artifacts (`model.pkl` or `tfidf_vectorizer.pkl`) not found!")
    st.markdown(
        """
        Please verify that the model has been trained before launching the application.
        Run the following command in your terminal:
        ```bash
        python train_model.py
        ```
        """
    )
    st.stop()


# ---------------------------------------------------------
# Sidebar Component
# ---------------------------------------------------------
with st.sidebar:
    # Brand Header
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 1.5rem; padding: 0.25rem 0;">
            <div style="background-color: #FACC15; color: #0B0B0B; font-weight: 900; font-size: 1.15rem; width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                TF
            </div>
            <div>
                <div style="font-size: 1.15rem; font-weight: 700; color: #F5F5F5; line-height: 1.1;">TicketFlow</div>
                <div style="font-size: 0.72rem; color: #FACC15; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase;">NLP Support Triage</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<p style='font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; color: #737373; margin-bottom: 0.5rem; font-weight: 600;'>Navigation</p>", unsafe_allow_html=True)

    # Navigation buttons
    nav_items = [
        ("Dashboard", "📊 Dashboard"),
        ("Classify Ticket", "⚡ Classify Ticket"),
        ("Ticket History", "📋 Ticket History"),
        ("About Project", "ℹ️ About Project")
    ]

    for page_key, page_label in nav_items:
        is_active = (st.session_state.active_page == page_key)
        btn_type = "primary" if is_active else "secondary"
        if st.button(page_label, key=f"nav_{page_key}", type=btn_type, use_container_width=True):
            set_page(page_key)

    st.markdown("<hr style='border: none; border-top: 1px solid #262626; margin: 1.5rem 0;'>", unsafe_allow_html=True)

    # User Profile / Authentication Section at Sidebar Bottom
    if st.session_state.authenticated_user:
        user = st.session_state.authenticated_user
        st.markdown(
            f"""
            <div class="tf-profile-card">
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <div style="width: 36px; height: 36px; border-radius: 50%; background-color: #262626; border: 1px solid #FACC15; display: flex; align-items: center; justify-content: center; font-weight: 600; color: #FACC15; font-size: 0.85rem;">
                        {user.get('full_name', 'U')[0].upper()}
                    </div>
                    <div style="overflow: hidden;">
                        <div style="font-size: 0.85rem; font-weight: 600; color: #F5F5F5; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">{user.get('full_name', 'Operator')}</div>
                        <div style="font-size: 0.72rem; color: #A3A3A3; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">{user.get('email', '')}</div>
                    </div>
                </div>
                <div style="margin-top: 0.6rem; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.68rem; background-color: #262626; color: #FACC15; padding: 0.15rem 0.5rem; border-radius: 4px; font-weight: 600;">ACTIVE AGENT</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.write("")
        if st.button("🚪 Sign Out", key="logout_btn", use_container_width=True):
            logout()
    else:
        st.markdown(
            """
            <div class="tf-profile-card">
                <div style="font-size: 0.85rem; font-weight: 600; color: #F5F5F5;">Guest Session</div>
                <div style="font-size: 0.75rem; color: #A3A3A3; margin-top: 0.2rem;">Sign in to log and triage tickets under your account.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.write("")
        col_auth1, col_auth2 = st.columns(2)
        with col_auth1:
            if st.button("Log In", key="nav_login", use_container_width=True):
                set_page("Login")
        with col_auth2:
            if st.button("Sign Up", key="nav_signup", use_container_width=True):
                set_page("Sign Up")


# =========================================================
# PAGE 1: DASHBOARD
# =========================================================
if st.session_state.active_page == "Dashboard":
    # Header
    col_dash_head, col_dash_btn = st.columns([3, 1])
    with col_dash_head:
        st.markdown("<h1 style='margin-bottom: 0.2rem;'>Welcome to TicketFlow</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 1.05rem; color: #A3A3A3; margin-top: 0;'>AI-powered support ticket classification and routing.</p>", unsafe_allow_html=True)
    with col_dash_btn:
        st.write("")
        if st.button("➕ Create New Ticket", type="primary", use_container_width=True):
            set_page("Classify Ticket")

    st.write("")

    # Real Metrics from SQLite Database
    metrics = get_metrics()

    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(
            f"""
            <div class="tf-card" style="margin-bottom: 0;">
                <div style="font-size: 0.75rem; color: #A3A3A3; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Total Tickets</div>
                <div style="font-size: 2.2rem; font-weight: 700; color: #FACC15; margin: 0.35rem 0;">{metrics['total']}</div>
                <div style="font-size: 0.75rem; color: #737373;">Persisted in SQLite</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m_col2:
        st.markdown(
            f"""
            <div class="tf-card" style="margin-bottom: 0;">
                <div style="font-size: 0.75rem; color: #A3A3A3; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">High Priority</div>
                <div style="font-size: 2.2rem; font-weight: 700; color: #EF4444; margin: 0.35rem 0;">{metrics['high']}</div>
                <div style="font-size: 0.75rem; color: #737373;">Urgent attention required</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m_col3:
        st.markdown(
            f"""
            <div class="tf-card" style="margin-bottom: 0;">
                <div style="font-size: 0.75rem; color: #A3A3A3; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Medium Priority</div>
                <div style="font-size: 2.2rem; font-weight: 700; color: #FACC15; margin: 0.35rem 0;">{metrics['medium']}</div>
                <div style="font-size: 0.75rem; color: #737373;">Standard queue triage</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m_col4:
        st.markdown(
            f"""
            <div class="tf-card" style="margin-bottom: 0;">
                <div style="font-size: 0.75rem; color: #A3A3A3; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Low Priority</div>
                <div style="font-size: 2.2rem; font-weight: 700; color: #22C55E; margin: 0.35rem 0;">{metrics['low']}</div>
                <div style="font-size: 0.75rem; color: #737373;">General inquiries & info</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # Recent Tickets Table
    st.markdown("### 📋 Recent Support Tickets")
    recent_tickets = get_tickets(limit=10)

    if recent_tickets:
        # Format table for display
        display_data = []
        for t in recent_tickets:
            summary = t["complaint"]
            if len(summary) > 75:
                summary = summary[:72] + "..."
            display_data.append({
                "Ticket ID": t["ticket_id"],
                "Timestamp": t["timestamp"],
                "Complaint Summary": summary,
                "Category": t["category"],
                "Priority": t["priority"],
                "Assigned Department": t["department"]
            })

        df_display = pd.DataFrame(display_data)
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        col_see_all, _ = st.columns([1, 4])
        with col_see_all:
            if st.button("View Full Ticket History →", use_container_width=True):
                set_page("Ticket History")
    else:
        st.markdown(
            """
            <div class="tf-card" style="text-align: center; padding: 2.5rem 1rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📭</div>
                <div style="font-size: 1.1rem; font-weight: 600; color: #F5F5F5;">No tickets registered yet</div>
                <div style="font-size: 0.85rem; color: #A3A3A3; margin-top: 0.25rem;">Create your first ticket to see real-time classification metrics.</div>
            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# PAGE 2: CLASSIFY TICKET
# =========================================================
elif st.session_state.active_page == "Classify Ticket":
    st.markdown("<h1 style='margin-bottom: 0.2rem;'>Classify a Support Ticket</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size: 1.05rem; color: #A3A3A3; margin-top: 0;'>"
        "Enter a customer complaint to identify its category, priority, and appropriate support department."
        "</p>",
        unsafe_allow_html=True
    )
    st.write("")

    # Presets / Quick Test Selector
    sample_presets = [
        "-- Select an example complaint or type your own below --",
        "The web app keeps crashing with a 500 internal server error when saving profile.",
        "I was charged twice on my credit card for this month's subscription and need an immediate refund.",
        "My account has been locked due to unauthorized login attempts and I forgot my password.",
        "The customer support representative was very rude and unhelpful on the phone call.",
        "Where can I find the official user guide documentation to learn the basic features?"
    ]

    selected_sample = st.selectbox(
        "Quick Test Presets (for viva / evaluation):",
        sample_presets,
        index=0
    )

    # When preset changes and is not default, populate preset_text
    current_default = ""
    if selected_sample != sample_presets[0]:
        current_default = selected_sample

    # Complaint text input
    with st.form("triage_form", clear_on_submit=False):
        complaint_text = st.text_area(
            "Customer Complaint Description:",
            value=current_default,
            height=130,
            placeholder="Type or paste the support complaint here (e.g., 'Server crashed during critical backup. Please resolve ASAP!')..."
        )

        col_submit, col_alt = st.columns([1, 4])
        with col_submit:
            submit_btn = st.form_submit_button("⚡ Classify Ticket", type="primary", use_container_width=True)

    if submit_btn:
        clean_text = complaint_text.strip()
        if not clean_text:
            st.warning("⚠️ Please enter a complaint description before submitting.")
        else:
            try:
                # 1. NLP Inference & Rule Execution
                result = classify_complaint(clean_text)

                # 2. Sequential Ticket ID generation
                new_id = get_next_ticket_id()
                active_email = st.session_state.authenticated_user["email"] if st.session_state.authenticated_user else "guest@ticketflow.io"

                # 3. Store persistently in SQLite
                add_ticket(
                    ticket_id=new_id,
                    user_email=active_email,
                    complaint=clean_text,
                    category=result["category"],
                    priority=result["priority"],
                    department=result["department"]
                )

                # 4. Save to session state to prevent rerun data loss
                st.session_state.last_classified = {
                    "ticket_id": new_id,
                    "complaint": clean_text,
                    "category": result["category"],
                    "priority": result["priority"],
                    "department": result["department"],
                    "confidence": result["confidence"],
                    "probabilities": result["probabilities"]
                }
                st.success("✅ Ticket classified and persisted successfully!")

            except Exception as e:
                st.error(f"Classification failed: {str(e)}")

    # Display Last Classified Result Cards
    if st.session_state.last_classified:
        res = st.session_state.last_classified

        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 1.25rem;">
                <div style="background-color: #FACC15; width: 6px; height: 26px; border-radius: 3px;"></div>
                <h2 style="margin: 0; color: #F5F5F5; font-size: 1.6rem; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase;">
                    FINAL PREDICTION
                </h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 1. Customer Complaint Card
        st.markdown(
            f"""
            <div class="tf-card" style="margin-bottom: 1.25rem; border-left: 4px solid #383838;">
                <div style="font-size: 0.75rem; color: #A3A3A3; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.35rem;">
                    Customer Complaint
                </div>
                <div style="font-size: 1.05rem; color: #F5F5F5; line-height: 1.5; font-style: italic;">
                    "{res['complaint']}"
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 2. Main Prediction Metrics Grid
        pred_col1, pred_col2 = st.columns([1.5, 1])

        with pred_col1:
            st.markdown(
                f"""
                <div class="tf-card tf-card-accent" style="height: 100%;">
                    <div style="font-size: 0.78rem; color: #A3A3A3; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em;">
                        Final Predicted Category
                    </div>
                    <div style="font-size: 2.3rem; font-weight: 800; color: #F5F5F5; margin: 0.2rem 0; letter-spacing: -0.02em;">
                        {res['category'].upper()}
                    </div>
                    <div style="display: flex; align-items: baseline; gap: 0.5rem; margin-top: 0.4rem;">
                        <span style="font-size: 0.88rem; color: #A3A3A3; font-weight: 500;">Prediction Confidence:</span>
                        <span style="font-size: 1.4rem; font-weight: 800; color: #FACC15;">{res.get('confidence', 0)}%</span>
                    </div>
                    <div style="font-size: 0.72rem; color: #737373; margin-top: 0.4rem;">
                        Extracted via TF-IDF Vectorization & Logistic Regression
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with pred_col2:
            st.markdown(
                f"""
                <div class="tf-card" style="height: 100%; border-left: 4px solid #FACC15;">
                    <div style="font-size: 0.78rem; color: #A3A3A3; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em;">
                        Assigned Department
                    </div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #F5F5F5; margin: 0.4rem 0 0.2rem 0;">
                        {res['department']}
                    </div>
                    <div style="font-size: 0.78rem; color: #A3A3A3; margin-top: 0.25rem;">
                        Automated Operational Routing Rule
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

        meta_col1, meta_col2 = st.columns(2)

        with meta_col1:
            p_class = "tf-badge-high" if res["priority"] == "High" else ("tf-badge-medium" if res["priority"] == "Medium" else "tf-badge-low")
            st.markdown(
                f"""
                <div class="tf-card" style="margin-bottom: 0;">
                    <div style="font-size: 0.75rem; color: #A3A3A3; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.4rem;">
                        Priority Level
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.6rem;">
                        <span class="tf-badge {p_class}" style="font-size: 0.95rem; padding: 0.35rem 0.85rem;">
                            {res['priority'].upper()} PRIORITY
                        </span>
                    </div>
                    <div style="font-size: 0.72rem; color: #737373; margin-top: 0.5rem;">
                        Keyword-based heuristic triage detection
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with meta_col2:
            st.markdown(
                f"""
                <div class="tf-card" style="margin-bottom: 0;">
                    <div style="font-size: 0.75rem; color: #A3A3A3; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.4rem;">
                        Ticket ID
                    </div>
                    <div style="font-size: 1.6rem; font-weight: 700; color: #FACC15;">
                        {res['ticket_id']}
                    </div>
                    <div style="font-size: 0.72rem; color: #737373; margin-top: 0.35rem;">
                        Persistently recorded in SQLite database
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Model Probability Distribution Breakdown
        if "probabilities" in res and res["probabilities"]:
            st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)
            st.markdown("#### 📊 Model Probability Distribution Across All Classes")
            p_cols = st.columns(len(res["probabilities"]))
            for idx, (cat_name, prob_val) in enumerate(res["probabilities"].items()):
                with p_cols[idx]:
                    is_winner = (cat_name == res["category"])
                    bar_color = "#FACC15" if is_winner else "#383838"
                    border_color = "#FACC15" if is_winner else "#303030"
                    st.markdown(
                        f"""
                        <div style="background-color: #171717; border: 1px solid {border_color}; border-radius: 8px; padding: 0.85rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 0.85rem; color: {'#FACC15' if is_winner else '#A3A3A3'}; font-weight: 600;">{cat_name.upper()}</span>
                                {'<span style="font-size: 0.65rem; background: #FACC15; color: #000; font-weight: 700; padding: 1px 5px; border-radius: 3px;">PREDICTED</span>' if is_winner else ''}
                            </div>
                            <div style="font-size: 1.25rem; font-weight: 700; color: {'#FACC15' if is_winner else '#F5F5F5'}; margin-top: 0.2rem;">{prob_val}%</div>
                            <div style="background-color: #262626; height: 5px; border-radius: 3px; margin-top: 0.5rem; overflow: hidden;">
                                <div style="background-color: {bar_color}; width: {prob_val}%; height: 100%;"></div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            st.caption("Note: Model confidence reflects Logistic Regression posterior probability and does not guarantee absolute factual correctness.")

        st.write("")
        col_reset, _ = st.columns([1, 4])
        with col_reset:
            if st.button("➕ Classify Another Ticket", use_container_width=True):
                st.session_state.last_classified = None
                st.rerun()


# =========================================================
# PAGE 3: TICKET HISTORY
# =========================================================
elif st.session_state.active_page == "Ticket History":
    st.markdown("<h1 style='margin-bottom: 0.2rem;'>Ticket History</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size: 1.05rem; color: #A3A3A3; margin-top: 0;'>"
        "Persistent audit log of all classified customer support tickets."
        "</p>",
        unsafe_allow_html=True
    )
    st.write("")

    # Filter Bar
    col_f1, col_f2, col_f3 = st.columns([2, 2, 4])

    with col_f1:
        cat_filter = st.selectbox(
            "Filter by Category:",
            ["All", "Technical", "Billing", "Account", "Service"]
        )

    with col_f2:
        prio_filter = st.selectbox(
            "Filter by Priority:",
            ["All", "High", "Medium", "Low"]
        )

    with col_f3:
        search_query = st.text_input(
            "Search Ticket ID or Complaint:",
            placeholder="Type ticket ID (e.g. TCK-101) or keywords..."
        )

    # Query SQLite database with filters
    tickets_data = get_tickets(
        category_filter=cat_filter,
        priority_filter=prio_filter,
        search_query=search_query
    )

    st.write("")

    if tickets_data:
        # Build DataFrame for table & download
        df_history = pd.DataFrame(tickets_data)
        df_history = df_history[["ticket_id", "timestamp", "complaint", "category", "priority", "department"]]
        df_history.columns = ["Ticket ID", "Date & Time", "Complaint Description", "Category", "Priority", "Assigned Department"]

        st.dataframe(df_history, use_container_width=True, hide_index=True)

        col_export, col_count = st.columns([2, 3])
        with col_export:
            csv_bytes = df_history.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download History as CSV",
                data=csv_bytes,
                file_name=f"ticketflow_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_count:
            st.markdown(
                f"<div style='text-align: right; color: #737373; font-size: 0.85rem; padding-top: 0.5rem;'>"
                f"Showing {len(tickets_data)} ticket record(s)"
                f"</div>",
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            """
            <div class="tf-card" style="text-align: center; padding: 2.5rem 1rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔍</div>
                <div style="font-size: 1.1rem; font-weight: 600; color: #F5F5F5;">No matching tickets found</div>
                <div style="font-size: 0.85rem; color: #A3A3A3; margin-top: 0.25rem;">Try adjusting your filter criteria or search query.</div>
            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# PAGE 4: ABOUT PROJECT
# =========================================================
elif st.session_state.active_page == "About Project":
    st.markdown("<h1 style='margin-bottom: 0.2rem;'>About TicketFlow</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size: 1.05rem; color: #A3A3A3; margin-top: 0;'>"
        "NLP-Based Support Ticket Classification and Automated Triaging System."
        "</p>",
        unsafe_allow_html=True
    )
    st.write("")

    # Card 1: Project Overview
    st.markdown(
        """
        <div class="tf-card tf-card-accent">
            <h3 style="margin-top: 0; color: #FACC15 !important;">🎯 Project Overview</h3>
            <p style="color: #D4D4D4; line-height: 1.6;">
                <strong>TicketFlow</strong> is an academic Natural Language Processing (NLP) micro-project designed to automate
                customer support operations. It eliminates manual triage overhead by processing incoming unstructured complaint text,
                predicting the correct domain category using Machine Learning, assessing urgency using keyword heuristics, and
                routing the ticket to the appropriate operational support department.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Card 2: Technology Stack
    st.markdown("### 🛠️ Technology Stack")
    t1, t2, t3 = st.columns(3)
    with t1:
        st.markdown(
            """
            <div class="tf-card">
                <div style="color: #FACC15; font-weight: 700; margin-bottom: 0.35rem;">NLP & Machine Learning</div>
                <div style="font-size: 0.85rem; color: #D4D4D4;">
                    • <strong>Scikit-Learn</strong><br>
                    • <strong>TF-IDF Vectorizer</strong> (ngram 1-2, 1000 features)<br>
                    • <strong>Logistic Regression</strong> (Stratified 80/20 split)
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with t2:
        st.markdown(
            """
            <div class="tf-card">
                <div style="color: #FACC15; font-weight: 700; margin-bottom: 0.35rem;">Application & UI</div>
                <div style="font-size: 0.85rem; color: #D4D4D4;">
                    • <strong>Python 3.12</strong><br>
                    • <strong>Streamlit</strong> with cached resources<br>
                    • <strong>Custom Black & Yellow CSS</strong> SaaS Design
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with t3:
        st.markdown(
            """
            <div class="tf-card">
                <div style="color: #FACC15; font-weight: 700; margin-bottom: 0.35rem;">Data & Persistence</div>
                <div style="font-size: 0.85rem; color: #D4D4D4;">
                    • <strong>SQLite 3</strong> (WAL mode enabled)<br>
                    • <strong>Pandas</strong> for tabular reporting<br>
                    • <strong>PBKDF2-HMAC-SHA256</strong> Password Hashing
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Card 3: System Pipeline Workflow
    st.markdown("### 🔄 NLP Processing Pipeline")
    st.markdown(
        """
        <div class="tf-card">
            <div style="display: flex; flex-direction: column; gap: 0.75rem; font-family: monospace; font-size: 0.85rem; color: #F5F5F5;">
                <div style="background-color: #202020; padding: 0.65rem 1rem; border-radius: 6px; border-left: 3px solid #FACC15;">
                    1. Customer Complaint Text Input ➔ Unstructured natural language string
                </div>
                <div style="text-align: center; color: #FACC15; font-weight: bold;">↓</div>
                <div style="background-color: #202020; padding: 0.65rem 1rem; border-radius: 6px; border-left: 3px solid #FACC15;">
                    2. TF-IDF Feature Extraction ➔ Unigrams & Bigrams converted into normalized numerical vector
                </div>
                <div style="text-align: center; color: #FACC15; font-weight: bold;">↓</div>
                <div style="background-color: #202020; padding: 0.65rem 1rem; border-radius: 6px; border-left: 3px solid #FACC15;">
                    3. Logistic Regression Classifier ➔ Calculates class probability distribution across 4 categories
                </div>
                <div style="text-align: center; color: #FACC15; font-weight: bold;">↓</div>
                <div style="background-color: #202020; padding: 0.65rem 1rem; border-radius: 6px; border-left: 3px solid #FACC15;">
                    4. Category Prediction ➔ Technical, Billing, Account, or Service
                </div>
                <div style="text-align: center; color: #FACC15; font-weight: bold;">↓</div>
                <div style="background-color: #202020; padding: 0.65rem 1rem; border-radius: 6px; border-left: 3px solid #FACC15;">
                    5. Rule-Based Priority Detection ➔ Keyword matching (High: critical/crash/security, Medium: error/delay, Low: general)
                </div>
                <div style="text-align: center; color: #FACC15; font-weight: bold;">↓</div>
                <div style="background-color: #202020; padding: 0.65rem 1rem; border-radius: 6px; border-left: 3px solid #FACC15;">
                    6. Automated Department Assignment ➔ Routes to designated support team
                </div>
                <div style="text-align: center; color: #FACC15; font-weight: bold;">↓</div>
                <div style="background-color: #202020; padding: 0.65rem 1rem; border-radius: 6px; border-left: 3px solid #FACC15;">
                    7. SQLite Persistent Storage ➔ Audited log with exportable CSV data
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Card 4: Architecture distinction
    st.markdown(
        """
        <div class="tf-card" style="border-left: 4px solid #22C55E;">
            <h4 style="margin-top: 0; color: #22C55E !important;">💡 ML Classification vs Rule-Based Priority</h4>
            <p style="color: #D4D4D4; font-size: 0.88rem; line-height: 1.5; margin-bottom: 0;">
                • <strong>Category Prediction (Machine Learning):</strong> Learns latent patterns from TF-IDF n-gram distributions.
                Achieved <strong>81.25% test accuracy</strong> on the benchmark dataset.<br>
                • <strong>Priority Detection (Rule-Based Heuristic):</strong> Employs explicit keyword triggers (e.g., <em>crash</em>, <em>unauthorized</em>, <em>overcharged</em>)
                to guarantee immediate escalation for safety, financial, and uptime incidents without stochastic prediction errors.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# PAGE 5: LOGIN
# =========================================================
elif st.session_state.active_page == "Login":
    st.markdown("<div style='max-width: 480px; margin: 0 auto;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #F5F5F5;'>Log in to TicketFlow</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #A3A3A3; margin-top: -0.5rem;'>Access your support operator workspace</p>", unsafe_allow_html=True)

    with st.form("login_form"):
        login_email = st.text_input("Email Address:", placeholder="operator@ticketflow.io")
        login_password = st.text_input("Password:", type="password", placeholder="Enter your password")

        submit_login = st.form_submit_button("Log In", type="primary", use_container_width=True)

    if submit_login:
        success, res = authenticate_user(login_email, login_password)
        if success:
            st.session_state.authenticated_user = res
            st.success(f"Welcome back, {res['full_name']}!")
            set_page("Dashboard")
        else:
            st.error(res)

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    # Demo Quick Access Helper
    st.markdown(
        """
        <div class="tf-card" style="padding: 1rem; text-align: center;">
            <div style="font-size: 0.8rem; color: #A3A3A3;">Quick Demo Account for Evaluation:</div>
            <div style="font-size: 0.85rem; color: #FACC15; font-weight: 600; margin-top: 0.2rem;">demo@ticketflow.io &nbsp;|&nbsp; demo123</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("Use Demo Account Credentials", use_container_width=True):
        success, res = authenticate_user("demo@ticketflow.io", "demo123")
        if success:
            st.session_state.authenticated_user = res
            set_page("Dashboard")

    st.write("")
    st.markdown("<div style='text-align: center; font-size: 0.85rem; color: #A3A3A3;'>Don't have an account yet?</div>", unsafe_allow_html=True)
    if st.button("Create an Account", use_container_width=True):
        set_page("Sign Up")

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# PAGE 6: SIGN UP
# =========================================================
elif st.session_state.active_page == "Sign Up":
    st.markdown("<div style='max-width: 480px; margin: 0 auto;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #F5F5F5;'>Create TicketFlow Account</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #A3A3A3; margin-top: -0.5rem;'>Set up your operator profile with local SQLite credentials</p>", unsafe_allow_html=True)

    with st.form("signup_form"):
        reg_name = st.text_input("Full Name:", placeholder="Alex Support")
        reg_email = st.text_input("Email Address:", placeholder="alex@ticketflow.io")
        reg_pwd = st.text_input("Password (min 6 characters):", type="password")
        reg_confirm = st.text_input("Confirm Password:", type="password")

        submit_signup = st.form_submit_button("Sign Up", type="primary", use_container_width=True)

    if submit_signup:
        if reg_pwd != reg_confirm:
            st.error("Passwords do not match.")
        else:
            ok, msg = register_user(reg_email, reg_pwd, reg_name)
            if ok:
                st.success(msg)
                # Automatically authenticate new user
                _, user_data = authenticate_user(reg_email, reg_pwd)
                st.session_state.authenticated_user = user_data
                set_page("Dashboard")
            else:
                st.error(msg)

    st.write("")
    st.markdown("<div style='text-align: center; font-size: 0.85rem; color: #A3A3A3;'>Already have an account?</div>", unsafe_allow_html=True)
    if st.button("Back to Login", use_container_width=True):
        set_page("Login")

    st.markdown("</div>", unsafe_allow_html=True)
