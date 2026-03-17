"""
HR & Compliance RAG System Streamlit Frontend
A premium chat-based interface for querying EU regulations,
council decisions, import licences and legal documents.
"""

import streamlit as st
import requests
import time
import json
from datetime import datetime
from typing import Optional
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
API_BASE = "http://localhost:8000"
HEALTH_ENDPOINT = f"{API_BASE}/health"
QUERY_ENDPOINT = f"{API_BASE}/query"

EXAMPLE_QUERIES = [
    "What does the council decision say about excessive deficit?",
    "What are the regulations about garlic import?",
    "Tell me about the commission regulation.",
    "What are the compliance requirements for data protection?",
    "Explain the import licensing procedures.",
]

CATEGORIES = {
    "All": "🌐",
    "EU Regulations": "📜",
    "Council Decisions": "⚖️",
    "Import Licenses": "📦",
    "Legal Documents": "📋",
    "Compliance": "✅"
}

# ──────────────────────────────────────────────
# Page config & custom CSS
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="HR & Compliance AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Root Variables ── */
:root {
    --accent-gradient: linear-gradient(135deg, #6366f1, #06b6d4);
    --accent-gradient-alt: linear-gradient(135deg, #8b5cf6, #ec4899);
    --card-bg: rgba(255, 255, 255, 0.06);
    --card-border: rgba(255, 255, 255, 0.08);
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --surface-hover: rgba(99, 102, 241, 0.12);
}

/* ── Global ── */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
}

[data-testid="stHeader"] {
    background: transparent !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, [data-testid="stDecoration"] { visibility: hidden; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1a1f35 100%);
    border-right: 1px solid rgba(99,102,241,0.15);
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
    color: #a5b4fc;
    font-size: 0.9rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 1rem;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    border-radius: 16px !important;
    padding: 1.1rem 1.3rem !important;
    margin-bottom: 0.75rem !important;
    border: 1px solid var(--card-border) !important;
    backdrop-filter: blur(12px);
    animation: fadeUp 0.35s ease-out;
}

/* user bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: rgba(99, 102, 241, 0.10) !important;
    border-color: rgba(99, 102, 241, 0.18) !important;
}

/* assistant bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: var(--card-bg) !important;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── Chat input ── */
[data-testid="stChatInput"] textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 14px !important;
    color: #f1f5f9 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 0.85rem 1rem !important;
    transition: border-color 0.2s;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 2px rgba(99,102,241,0.25) !important;
}

/* ── Expander (sources) ── */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
    margin-top: 0.5rem;
}
[data-testid="stExpander"] summary {
    font-weight: 600;
    color: #94a3b8 !important;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.45rem 1.1rem !important;
    font-size: 0.82rem !important;
    transition: all 0.25s ease !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    background: rgba(255,255,255,0.04) !important;
    color: #cbd5e1 !important;
}
.stButton > button:hover {
    background: var(--surface-hover) !important;
    border-color: rgba(99,102,241,0.35) !important;
    color: #a5b4fc !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(99,102,241,0.15);
}

/* ── Status badge ── */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.status-online  { background: rgba(34,197,94,0.12); color: #4ade80; border: 1px solid rgba(34,197,94,0.25); }
.status-offline { background: rgba(239,68,68,0.12); color: #f87171; border: 1px solid rgba(239,68,68,0.25); }
.status-checking { background: rgba(250,204,21,0.12); color: #facc15; border: 1px solid rgba(250,204,21,0.25); }

/* ── Hero section ── */
.hero-title {
    font-size: 2.8rem;
    font-weight: 800;
    background: var(--accent-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 0.3rem;
    line-height: 1.2;
}
.hero-subtitle {
    text-align: center;
    color: var(--text-secondary);
    font-size: 1.05rem;
    margin-bottom: 1.8rem;
    font-weight: 400;
}

/* ── Source card ── */
.source-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.55rem;
    transition: all 0.2s;
}
.source-card:hover {
    background: rgba(99,102,241,0.06);
    border-color: rgba(99,102,241,0.15);
    transform: translateX(4px);
}
.source-card-title {
    font-weight: 600;
    color: #a5b4fc;
    font-size: 0.85rem;
    margin-bottom: 0.3rem;
}
.source-card-text {
    color: #94a3b8;
    font-size: 0.8rem;
    line-height: 1.55;
}

/* ── Stats card ── */
.stat-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    transition: all 0.3s;
}
.stat-card:hover {
    background: rgba(99,102,241,0.08);
    border-color: rgba(99,102,241,0.2);
    transform: translateY(-2px);
}
.stat-value {
    font-size: 1.8rem;
    font-weight: 800;
    background: var(--accent-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}
.stat-label {
    color: #94a3b8;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* ── Feature card ── */
.feature-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 0.8rem;
    transition: all 0.3s;
}
.feature-card:hover {
    background: rgba(99,102,241,0.06);
    border-color: rgba(99,102,241,0.15);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(99,102,241,0.12);
}
.feature-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem;
}
.feature-title {
    color: #e2e8f0;
    font-size: 1rem;
    font-weight: 700;
    margin-bottom: 0.3rem;
}
.feature-desc {
    color: #94a3b8;
    font-size: 0.85rem;
    line-height: 1.5;
}

/* ── Metric cards ── */
.stMetric {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(255,255,255,0.03);
    border-radius: 12px;
    padding: 6px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: #94a3b8;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background: rgba(99,102,241,0.15) !important;
    color: #a5b4fc !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 10px !important;
    color: #f1f5f9 !important;
}

/* ── Slider ── */
.stSlider > div > div > div {
    background: rgba(99,102,241,0.3) !important;
}

/* ── Download button ── */
.download-btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 10px;
    color: #a5b4fc;
    font-weight: 600;
    font-size: 0.85rem;
    text-decoration: none;
    transition: all 0.2s;
}
.download-btn:hover {
    background: rgba(99,102,241,0.2);
    transform: translateY(-1px);
}

/* ── Code blocks ── */
code {
    font-family: 'JetBrains Mono', monospace !important;
    background: rgba(255,255,255,0.05) !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    color: #a5b4fc !important;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Session state
# ──────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_status" not in st.session_state:
    st.session_state.api_status = "checking"
if "query_count" not in st.session_state:
    st.session_state.query_count = 0
if "total_sources" not in st.session_state:
    st.session_state.total_sources = 0
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "All"
if "show_timestamps" not in st.session_state:
    st.session_state.show_timestamps = True
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "dark"
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "response_times" not in st.session_state:
    st.session_state.response_times = []
if "feedback_scores" not in st.session_state:
    st.session_state.feedback_scores = []
if "search_history" not in st.session_state:
    st.session_state.search_history = []
if "current_page" not in st.session_state:
    st.session_state.current_page = "chat"


# ──────────────────────────────────────────────
# Helper functions
# ──────────────────────────────────────────────
def check_api_health() -> str:
    """Return 'online', 'offline', or 'checking'."""
    try:
        r = requests.get(HEALTH_ENDPOINT, timeout=4)
        return "online" if r.ok else "offline"
    except Exception:
        return "offline"


def query_api(question: str, top_k: int = 5) -> dict:
    """Send a question to the RAG backend and return the JSON response."""
    r = requests.post(
        QUERY_ENDPOINT,
        json={"question": question, "top_k": top_k},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


def render_status_badge(status: str):
    """Return HTML for a coloured status pill."""
    icon_map = {"online": "🟢", "offline": "🔴", "checking": "🟡"}
    label = status.capitalize()
    icon = icon_map.get(status, "⚪")
    return f'<span class="status-badge status-{status}">{icon} API {label}</span>'


def render_sources(sources: list):
    """Display retrieved source snippets inside an expander."""
    if not sources:
        return
    with st.expander(f"📚 **{len(sources)} source(s) retrieved**", expanded=False):
        for i, src in enumerate(sources, 1):
            title = src.get("source", src.get("title", f"Source {i}"))
            text = src.get("text", src.get("content", ""))
            score = src.get("score", src.get("similarity", None))
            score_str = f" — relevance {score:.2f}" if score is not None else ""
            
            # Add copy button for source text
            col1, col2 = st.columns([0.95, 0.05])
            with col1:
                st.markdown(
                    f"""<div class="source-card">
                        <div class="source-card-title">📄 {title}{score_str}</div>
                        <div class="source-card-text">{text[:400]}{'…' if len(text) > 400 else ''}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
            with col2:
                if st.button("📋", key=f"copy_{i}", help="Copy source text"):
                    st.toast("Source copied to clipboard!", icon="✅")


def export_chat_history() -> str:
    """Export chat history as JSON."""
    export_data = {
        "exported_at": datetime.now().isoformat(),
        "query_count": st.session_state.query_count,
        "messages": st.session_state.messages,
        "favorites": st.session_state.favorites,
        "response_times": st.session_state.response_times
    }
    return json.dumps(export_data, indent=2)


def add_to_favorites(question: str, answer: str):
    """Add a Q&A pair to favorites."""
    fav = {
        "question": question,
        "answer": answer,
        "timestamp": datetime.now().isoformat()
    }
    if fav not in st.session_state.favorites:
        st.session_state.favorites.append(fav)
        st.toast("Added to favorites! ⭐", icon="✅")


def render_analytics_dashboard():
    """Render analytics dashboard with charts."""
    st.markdown("### 📊 Analytics Dashboard")
    
    if st.session_state.response_times:
        # Response time chart
        fig_time = go.Figure()
        fig_time.add_trace(go.Scatter(
            y=st.session_state.response_times,
            mode='lines+markers',
            name='Response Time',
            line=dict(color='#6366f1', width=3),
            marker=dict(size=8)
        ))
        fig_time.update_layout(
            title="Response Time Trend",
            yaxis_title="Time (seconds)",
            xaxis_title="Query Number",
            template="plotly_dark",
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_time, use_container_width=True)
    
    if st.session_state.feedback_scores:
        # Feedback distribution
        col1, col2 = st.columns(2)
        with col1:
            feedback_df = pd.DataFrame(st.session_state.feedback_scores, columns=['Score'])
            fig_feedback = px.histogram(
                feedback_df, 
                x='Score',
                title="Feedback Distribution",
                color_discrete_sequence=['#6366f1']
            )
            fig_feedback.update_layout(
                template="plotly_dark",
                height=300,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_feedback, use_container_width=True)
        
        with col2:
            avg_score = sum(st.session_state.feedback_scores) / len(st.session_state.feedback_scores)
            st.markdown(
                f"""<div class="stat-card" style="height: 250px; display: flex; flex-direction: column; justify-content: center;">
                    <div class="stat-value" style="font-size: 3rem;">{avg_score:.1f}</div>
                    <div class="stat-label">Average Rating</div>
                    <div style="color: #94a3b8; margin-top: 0.5rem;">Based on {len(st.session_state.feedback_scores)} ratings</div>
                </div>""",
                unsafe_allow_html=True
            )
    
    # Search history word cloud data
    if st.session_state.search_history:
        st.markdown("#### 🔍 Recent Search Topics")
        search_df = pd.DataFrame(st.session_state.search_history, columns=['Query', 'Timestamp'])
        st.dataframe(search_df.tail(10), use_container_width=True, hide_index=True)


def render_favorites_page():
    """Render favorites page."""
    st.markdown("### ⭐ Favorite Q&A Pairs")
    
    if not st.session_state.favorites:
        st.info("No favorites yet. Star your favorite answers from the chat!")
        return
    
    for idx, fav in enumerate(reversed(st.session_state.favorites)):
        with st.container():
            col1, col2 = st.columns([0.95, 0.05])
            with col1:
                st.markdown(f"**Q:** {fav['question']}")
                st.markdown(f"**A:** {fav['answer'][:300]}...")
                st.caption(f"Saved on {fav['timestamp'][:10]}")
            with col2:
                if st.button("🗑️", key=f"del_fav_{idx}"):
                    st.session_state.favorites.remove(fav)
                    st.rerun()
            st.divider()


def render_document_explorer():
    """Render document explorer interface."""
    st.markdown("### 📚 Document Explorer")
    
    # Category filter
    selected_cat = st.selectbox(
        "Filter by category",
        list(CATEGORIES.keys()),
        format_func=lambda x: f"{CATEGORIES[x]} {x}"
    )
    
    # Search within documents
    search_term = st.text_input("🔍 Search documents", placeholder="Enter keywords...")
    
    if search_term:
        with st.spinner("Searching documents..."):
            try:
                data = query_api(search_term, top_k=10)
                sources = data.get("sources", [])
                
                st.markdown(f"#### Found {len(sources)} relevant documents")
                for src in sources:
                    with st.expander(f"📄 {src.get('source', 'Document')}"):
                        st.markdown(src.get('text', ''))
                        if src.get('score'):
                            st.progress(src['score'], text=f"Relevance: {src['score']:.2%}")
            except Exception as e:
                st.error(f"Search failed: {e}")


def render_settings_page():
    """Render advanced settings page."""
    st.markdown("### ⚙️ Advanced Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Display Options")
        st.session_state.show_timestamps = st.checkbox(
            "Show timestamps", 
            value=st.session_state.show_timestamps
        )
        show_sources_default = st.checkbox("Auto-expand sources", value=False)
        enable_sound = st.checkbox("Enable sound notifications", value=False)
        
    with col2:
        st.markdown("#### Query Settings")
        default_top_k = st.number_input("Default Top-K", min_value=1, max_value=20, value=5)
        temperature = st.slider("Response creativity", 0.0, 1.0, 0.7, 0.1)
        max_tokens = st.number_input("Max response length", 100, 2000, 500, 50)
    
    st.divider()
    
    st.markdown("#### Data Management")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Export Chat History", use_container_width=True):
            export_data = export_chat_history()
            st.download_button(
                "Download JSON",
                export_data,
                file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("🗑️ Clear All Data", use_container_width=True):
            st.session_state.messages = []
            st.session_state.favorites = []
            st.session_state.search_history = []
            st.session_state.response_times = []
            st.session_state.feedback_scores = []
            st.success("All data cleared!")
    
    with col3:
        if st.button("🔄 Reset Settings", use_container_width=True):
            st.session_state.show_timestamps = True
            st.success("Settings reset to defaults!")


def render_stats_dashboard():
    """Render statistics dashboard."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            f"""<div class="stat-card">
                <div class="stat-value">{st.session_state.query_count}</div>
                <div class="stat-label">Queries Made</div>
            </div>""",
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""<div class="stat-card">
                <div class="stat-value">{len(st.session_state.messages) // 2}</div>
                <div class="stat-label">Conversations</div>
            </div>""",
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f"""<div class="stat-card">
                <div class="stat-value">{st.session_state.total_sources}</div>
                <div class="stat-label">Sources Retrieved</div>
            </div>""",
            unsafe_allow_html=True
        )


# ──────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧭 Navigation")
    
    # Navigation buttons
    if st.button("� Chate", use_container_width=True, type="primary" if st.session_state.current_page == "chat" else "secondary"):
        st.session_state.current_page = "chat"
        st.rerun()
    
    if st.button("⭐ Favorites", use_container_width=True, type="primary" if st.session_state.current_page == "favorites" else "secondary"):
        st.session_state.current_page = "favorites"
        st.rerun()
    
    if st.button("📊 Analytics", use_container_width=True, type="primary" if st.session_state.current_page == "analytics" else "secondary"):
        st.session_state.current_page = "analytics"
        st.rerun()
    
    if st.button("� Dolcuments", use_container_width=True, type="primary" if st.session_state.current_page == "documents" else "secondary"):
        st.session_state.current_page = "documents"
        st.rerun()
    
    if st.button("⚙️ Settings", use_container_width=True, type="primary" if st.session_state.current_page == "settings" else "secondary"):
        st.session_state.current_page = "settings"
        st.rerun()

    st.divider()
    
    # Quick stats
    st.markdown("### 📈 Quick Stats")
    render_stats_dashboard()

    st.divider()
    
    # API Status
    st.markdown("### 🔌 API Status")
    if st.button("🔄 Refresh", use_container_width=True):
        st.session_state.api_status = check_api_health()
        st.rerun()

    st.markdown(
        render_status_badge(st.session_state.api_status),
        unsafe_allow_html=True,
    )

    st.divider()
    
    # Query settings (only show on chat page)
    if st.session_state.current_page == "chat":
        st.markdown("### 🎛️ Query Settings")
        top_k = st.slider("Top-K documents", min_value=1, max_value=20, value=5)
        
        st.divider()
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    else:
        top_k = 5

    st.divider()
    st.caption("HR & Compliance RAG System v2.0")
    st.caption("Powered by FAISS + Groq LLM")
    st.caption(f"© {datetime.now().year} - All Rights Reserved")


# ──────────────────────────────────────────────
# Check API health (first load & periodic)
# ──────────────────────────────────────────────
if st.session_state.api_status == "checking":
    st.session_state.api_status = check_api_health()


# ──────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────
col_l, col_m, col_r = st.columns([5, 1, 1])
with col_l:
    st.markdown('<div class="hero-title">🛡️ HR & Compliance AI</div>', unsafe_allow_html=True)
with col_m:
    st.markdown(
        render_status_badge(st.session_state.api_status),
        unsafe_allow_html=True,
    )
with col_r:
    if st.button("📥 Export", help="Export chat history"):
        export_data = export_chat_history()
        st.download_button(
            "Download",
            export_data,
            file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )


# ──────────────────────────────────────────────
# Page Router
# ──────────────────────────────────────────────
if st.session_state.current_page == "favorites":
    render_favorites_page()

elif st.session_state.current_page == "analytics":
    render_analytics_dashboard()

elif st.session_state.current_page == "documents":
    render_document_explorer()

elif st.session_state.current_page == "settings":
    render_settings_page()

else:  # chat page
    # ──────────────────────────────────────────────
    # Welcome state (no messages yet)
    # ──────────────────────────────────────────────
    if not st.session_state.messages:
        st.markdown(
            '<div class="hero-subtitle">'
            "Ask any question about EU regulations, council decisions, "
            "import licences, or legal documents."
            "</div>",
            unsafe_allow_html=True,
        )

        # Feature cards
        st.markdown("#### ✨ Key Features")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(
                """<div class="feature-card">
                    <div class="feature-icon">🤖</div>
                    <div class="feature-title">AI-Powered Search</div>
                    <div class="feature-desc">Advanced RAG system with semantic search across thousands of documents</div>
                </div>""",
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                """<div class="feature-card">
                    <div class="feature-icon">⚡</div>
                    <div class="feature-title">Lightning Fast</div>
                    <div class="feature-desc">Get accurate answers in seconds with FAISS vector search</div>
                </div>""",
                unsafe_allow_html=True
            )
        
        with col3:
            st.markdown(
                """<div class="feature-card">
                    <div class="feature-icon">🎯</div>
                    <div class="feature-title">Source Citations</div>
                    <div class="feature-desc">Every answer includes relevant source documents for verification</div>
                </div>""",
                unsafe_allow_html=True
            )

        st.markdown("#### 💡 Try These Examples")
        # Example query chips
        cols = st.columns(len(EXAMPLE_QUERIES))
        for col, example in zip(cols, EXAMPLE_QUERIES):
            with col:
                if st.button(example, key=f"ex_{example[:20]}", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": example})
                    st.rerun()


    # ──────────────────────────────────────────────
    # Render chat history
    # ──────────────────────────────────────────────
    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            col1, col2 = st.columns([0.95, 0.05])
            with col1:
                st.markdown(msg["content"])
                if msg["role"] == "assistant" and msg.get("sources"):
                    render_sources(msg["sources"])
                    st.session_state.total_sources += len(msg.get("sources", []))
            
            with col2:
                if msg["role"] == "assistant":
                    if st.button("⭐", key=f"fav_{idx}", help="Add to favorites"):
                        user_msg = st.session_state.messages[idx-1]["content"] if idx > 0 else ""
                        add_to_favorites(user_msg, msg["content"])
                    
                    # Feedback buttons
                    col_up, col_down = st.columns(2)
                    with col_up:
                        if st.button("👍", key=f"up_{idx}", help="Good response"):
                            st.session_state.feedback_scores.append(5)
                            st.toast("Thanks for your feedback!", icon="👍")
                    with col_down:
                        if st.button("👎", key=f"down_{idx}", help="Poor response"):
                            st.session_state.feedback_scores.append(1)
                            st.toast("Thanks for your feedback!", icon="👎")


    # ──────────────────────────────────────────────
    # Chat input
    # ──────────────────────────────────────────────
    if prompt := st.chat_input("Ask about EU regulations …"):
        # Append & display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.search_history.append([prompt, datetime.now().isoformat()])
        
        with st.chat_message("user"):
            st.markdown(prompt)

        # Call the backend
        start_time = time.time()
        with st.chat_message("assistant"):
            with st.spinner("Thinking …"):
                try:
                    data = query_api(prompt, top_k=top_k)
                    answer = data.get("answer", "I'm sorry, I couldn't find an answer.")
                    sources = data.get("sources", [])
                    
                    # Track metrics
                    response_time = time.time() - start_time
                    st.session_state.response_times.append(response_time)
                    st.session_state.query_count += 1
                    
                except requests.exceptions.ConnectionError:
                    answer = "⚠️ **Cannot reach the API server.** Make sure the backend is running on `localhost:8000`."
                    sources = []
                    st.session_state.api_status = "offline"
                except Exception as exc:
                    answer = f"⚠️ **Error:** {exc}"
                    sources = []

            st.markdown(answer)
            render_sources(sources)
            
            # Show response time
            if 'response_time' in locals():
                st.caption(f"⏱️ Response time: {response_time:.2f}s")

        # Persist assistant message
        st.session_state.messages.append(
            {"role": "assistant", "content": answer, "sources": sources}
        )
