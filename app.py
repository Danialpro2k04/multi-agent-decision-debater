import streamlit as st
from debate_team import run_decision_debate
import json
import time
import threading


# PAGE CONFIG
st.set_page_config(
    page_title="AI Decision Debater",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# SESSION STATE
if "debate_count" not in st.session_state:
    st.session_state.debate_count = 0
if "last_confidence" not in st.session_state:
    st.session_state.last_confidence = None
if "result" not in st.session_state:
    st.session_state.result = None
if "verdict" not in st.session_state:
    st.session_state.verdict = None
if "show_results" not in st.session_state:
    st.session_state.show_results = False
if "decision_text" not in st.session_state:
    st.session_state.decision_text = ""
if "context_text" not in st.session_state:
    st.session_state.context_text = ""
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "judge_harshness" not in st.session_state:
    st.session_state.judge_harshness = 3
if "exclude_optimist" not in st.session_state:
    st.session_state.exclude_optimist = False
if "exclude_devil" not in st.session_state:
    st.session_state.exclude_devil = False
if "exclude_risk" not in st.session_state:
    st.session_state.exclude_risk = False
if "exclude_research" not in st.session_state:
    st.session_state.exclude_research = False

# MASTER CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ══════════════════════════════════════════
   1. GLOBAL THEMING
══════════════════════════════════════════ */
html, body, [class*="css"], .stApp, .block-container {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background: #0b0f19 !important;
    position: relative !important;
}
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 100vh;
    background: radial-gradient(circle at 50% 0%, rgba(99,102,241,0.15), transparent 50%);
    pointer-events: none;
    z-index: 0;
}
[data-testid="stAppViewContainer"] > .block-container {
    position: relative;
    z-index: 1;
}

/* Keep header transparent for the sidebar toggle, but hide the menu, footer, and deploy button */
#MainMenu, footer { visibility: hidden !important; }
header { background: transparent !important; }
.stDeployButton, .stAppDeployButton, [data-testid="stAppDeployButton"] { 
    display: none !important; 
}

.block-container {
    padding: 2rem 2rem 4rem !important;
    max-width: 1100px !important;
}

h1, h2, h3, h4, h5, h6, p, span, label, div {
    color: inherit;
}

/* ══════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: #0d1117 !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1rem !important;
}
.sb-title {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.28);
    margin-bottom: 0.75rem;
}
.sb-agent {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0.55rem 0.7rem;
    border-radius: 10px;
    margin-bottom: 0.3rem;
    transition: background 0.2s;
}
.sb-agent:hover { background: rgba(255,255,255,0.04); }
.sb-agent-icon {
    width: 30px; height: 30px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.95rem;
    flex-shrink: 0;
}
.sb-agent-name {
    font-size: 0.82rem;
    font-weight: 600;
    color: rgba(255,255,255,0.85);
}
.sb-agent-role {
    font-size: 0.7rem;
    color: rgba(255,255,255,0.32);
    margin-top: 1px;
}
.sb-divider {
    height: 1px;
    background: rgba(255,255,255,0.06);
    margin: 1.2rem 0;
}
.sb-stat-row { display: flex; gap: 0.5rem; margin-top: 0.5rem; }
.sb-stat {
    flex: 1;
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 0.7rem 0.5rem;
    text-align: center;
}
.sb-stat-val {
    font-size: 1.3rem;
    font-weight: 800;
    color: #818cf8;
    line-height: 1;
}
.sb-stat-lbl {
    font-size: 0.62rem;
    color: rgba(255,255,255,0.32);
    font-weight: 600;
    letter-spacing: 0.5px;
    margin-top: 0.3rem;
    text-transform: uppercase;
}

/* ══════════════════════════════════════════
   HERO
══════════════════════════════════════════ */
.hero {
    text-align: center;
    margin-bottom: 2rem;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 50px;
    padding: 5px 16px;
    font-size: 0.72rem;
    font-weight: 600;
    color: #818cf8;
    margin-bottom: 1.25rem;
}
.hero h1 {
    font-size: clamp(2rem, 5vw, 3.2rem) !important;
    font-weight: 900 !important;
    line-height: 1.1 !important;
    letter-spacing: -1.5px !important;
    color: #ffffff !important;
    margin-bottom: 1rem !important;
}
.hero h1 span {
    background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-subtitle {
    font-size: 1.05rem !important;
    color: #94a3b8 !important;
    font-weight: 400 !important;
    line-height: 1.6 !important;
    max-width: 600px !important;
    margin: 0 auto 0 !important;
}

/* ══════════════════════════════════════════
   2. AGENT SHOWCASE CARDS
══════════════════════════════════════════ */
.agent-showcase-card {
    background: #111827;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 15px;
    text-align: center;
    transition: transform 0.2s ease, background 0.2s ease, border-color 0.2s ease;
    cursor: default;
    height: 140px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.agent-showcase-card:hover {
    transform: translateY(-5px);
    background: #1e293b;
    border-color: rgba(139,92,246,0.3);
}
.agent-showcase-emoji {
    font-size: 1.8rem;
    margin-bottom: 8px;
    display: block;
}
.agent-showcase-name {
    font-size: 0.82rem;
    font-weight: 700;
    color: #f1f5f9;
    margin-bottom: 4px;
}
.agent-showcase-role {
    font-size: 0.68rem;
    color: #64748b;
    line-height: 1.3;
}

/* ══════════════════════════════════════════
   3. TEXT AREA STYLING
══════════════════════════════════════════ */
.stTextArea textarea {
    background: #131b2c !important;
    color: #f8fafc !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 14px 16px !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    line-height: 1.6 !important;
}
.stTextArea textarea::placeholder {
    color: #475569 !important;
}
.stTextArea textarea:focus {
    border-color: #8b5cf6 !important;
    box-shadow: 0 0 0 2px rgba(139,92,246,0.2) !important;
    outline: none !important;
}
.stTextArea label p {
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    color: #94a3b8 !important;
    letter-spacing: 0.3px !important;
    margin-bottom: 6px !important;
}

/* ══════════════════════════════════════════
   4. EXPANDER
══════════════════════════════════════════ */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 10px !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    color: #cbd5e1 !important;
    padding: 0.75rem 1rem !important;
}
.streamlit-expanderHeader:hover {
    background: rgba(255,255,255,0.06) !important;
    border-color: rgba(139,92,246,0.25) !important;
}
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 12px !important;
}

/* Slider */
.stSlider > div > div > div > div {
    background-color: #8b5cf6 !important;
}
.stSlider label p {
    color: #94a3b8 !important;
    font-size: 0.82rem !important;
}

/* Checkbox */
.stCheckbox label p {
    color: #cbd5e1 !important;
    font-size: 0.82rem !important;
}
.stCheckbox label span[data-testid="stCheckboxCheck"] {
    border-color: rgba(255,255,255,0.2) !important;
    background: #131b2c !important;
}
.stCheckbox label span[data-testid="stCheckboxCheck"][aria-checked="true"] {
    background: #6366f1 !important;
    border-color: #6366f1 !important;
}

/* ══════════════════════════════════════════
   5. PRIMARY CTA BUTTON
══════════════════════════════════════════ */
.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 12px 24px !important;
    width: 100% !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    font-family: 'Inter', sans-serif !important;
    box-shadow: 0 4px 15px rgba(168,85,247,0.4) !important;
    transition: all 0.22s ease !important;
    letter-spacing: 0.3px !important;
}
.stButton > button[kind="primary"]:hover {
    filter: brightness(1.1) !important;
    transform: scale(1.02) !important;
    box-shadow: 0 6px 25px rgba(168,85,247,0.55) !important;
}
.stButton > button[kind="primary"]:active {
    transform: scale(1.0) !important;
    filter: brightness(0.95) !important;
}

/* Secondary button (new debate) */
.stButton > button:not([kind="primary"]) {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #94a3b8 !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
}
.stButton > button:not([kind="primary"]):hover {
    background: rgba(255,255,255,0.08) !important;
    color: #e2e8f0 !important;
}

/* ══════════════════════════════════════════
   6. RECENT DEBATES MOCK CARDS
══════════════════════════════════════════ */
.recent-card {
    background: #111827;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 14px;
    padding: 24px;
    height: 100%;
    display: flex;
    flex-direction: column;
    transition: border-color 0.2s, transform 0.2s;
}
.recent-card:hover {
    border-color: rgba(139,92,246,0.3);
    transform: translateY(-2px);
}
.recent-card-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #f1f5f9;
    margin-bottom: 10px;
    line-height: 1.3;
}
.recent-card-body {
    font-size: 0.82rem;
    color: #64748b;
    line-height: 1.6;
    flex: 1;
    margin-bottom: 16px;
}
.conf-pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: rgba(34,197,94,0.15);
    color: #4ade80;
    padding: 4px 10px;
    border-radius: 99px;
    font-size: 0.72rem;
    font-weight: 600;
}
.conf-pill.amber {
    background: rgba(251,191,36,0.15);
    color: #fbbf24;
}
.conf-pill.red {
    background: rgba(239,68,68,0.15);
    color: #f87171;
}

/* ══════════════════════════════════════════
   PROGRESS SCREEN
══════════════════════════════════════════ */
.progress-wrap { text-align: center; padding: 3.5rem 2rem; }
.progress-stage-icon {
    font-size: 3.5rem; margin-bottom: 1.1rem; display: block;
    animation: float 2s ease-in-out infinite;
}
@keyframes float {
    0%,100%{transform:translateY(0)}
    50%{transform:translateY(-8px)}
}
.progress-stage-title {
    font-size: 1.35rem; font-weight: 700; color: white; margin-bottom: 0.4rem;
}
.progress-stage-sub {
    font-size: 0.87rem; color: #64748b; margin-bottom: 2.25rem;
}
.progress-dots {
    display: flex; justify-content: center; gap: 8px; margin-bottom: 1.75rem;
}
.progress-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: rgba(255,255,255,0.12); display: inline-block;
    transition: all 0.3s;
}
.progress-dot.active {
    background: #8b5cf6; box-shadow: 0 0 8px rgba(139,92,246,0.7);
}
.progress-dot.done { background: #34d399; }
.progress-agent-list {
    display: flex; justify-content: center; gap: 8px; flex-wrap: wrap;
}
.progress-agent-chip {
    display: flex; align-items: center; gap: 5px;
    background: rgba(255,255,255,0.035); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 50px; padding: 5px 12px; font-size: 0.73rem;
    color: rgba(255,255,255,0.3); font-weight: 500; transition: all 0.3s;
}
.progress-agent-chip.active {
    background: rgba(139,92,246,0.15); border-color: rgba(139,92,246,0.45);
    color: #c4b5fd; box-shadow: 0 0 10px rgba(139,92,246,0.2);
}
.progress-agent-chip.done {
    background: rgba(52,211,153,0.1); border-color: rgba(52,211,153,0.3);
    color: #34d399;
}

/* ══════════════════════════════════════════
   RESULTS
══════════════════════════════════════════ */
.results-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem;
}
.results-title { font-size: 1.5rem; font-weight: 800; color: #f1f5f9; }
.results-meta { display: flex; gap: 8px; }
.results-chip {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 8px; padding: 4px 12px; font-size: 0.72rem;
    color: #64748b; font-weight: 500;
}

.verdict-banner {
    background: linear-gradient(135deg, rgba(99,102,241,0.12), rgba(168,85,247,0.12));
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 16px; padding: 2rem; margin-bottom: 1.25rem;
    position: relative; overflow: hidden;
}
.verdict-banner::after {
    content:'⚖️'; position:absolute; right:1.5rem; top:50%;
    transform:translateY(-50%); font-size:4rem; opacity:0.06;
}
.verdict-eyebrow {
    font-size: 0.68rem; font-weight: 700; letter-spacing: 2px;
    text-transform: uppercase; color: #818cf8; margin-bottom: 0.7rem;
}
.verdict-main {
    font-size: clamp(1.3rem,3vw,1.85rem); font-weight: 800; color: white;
    line-height: 1.2; letter-spacing: -0.5px; max-width: 85%;
}
.verdict-conf-row {
    display: flex; align-items: center; gap: 12px; margin-top: 1.2rem;
}
.conf-label {
    font-size: 0.72rem; color: #64748b; font-weight: 600; white-space: nowrap;
}
.conf-track {
    flex: 1; height: 5px; background: rgba(255,255,255,0.08);
    border-radius: 50px; overflow: hidden;
}
.conf-fill {
    height: 100%; border-radius: 50px;
    background: linear-gradient(90deg,#6366f1,#a855f7,#ec4899);
}
.conf-pct {
    font-size: 0.85rem; font-weight: 700; color: #818cf8; white-space: nowrap;
}

.info-grid {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 1rem; margin-bottom: 1.25rem;
}
@media(max-width:700px){.info-grid{grid-template-columns:1fr;}}
.info-card {
    background: rgba(255,255,255,0.025); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px; padding: 1.25rem;
}
.info-card-label {
    font-size: 0.65rem; font-weight: 700; letter-spacing: 1.5px;
    text-transform: uppercase; margin-bottom: 0.85rem;
    display: flex; align-items: center; gap: 6px;
}
.info-item {
    display: flex; align-items: flex-start; gap: 8px;
    padding: 0.45rem 0; border-bottom: 1px solid rgba(255,255,255,0.04);
    font-size: 0.85rem; color: rgba(255,255,255,0.75); line-height: 1.5;
}
.info-item:last-child{border-bottom:none;padding-bottom:0;}
.info-marker{flex-shrink:0;margin-top:3px;font-size:0.72rem;}

.assumption-row {
    display: flex; align-items: flex-start; gap: 8px;
    background: rgba(251,191,36,0.06); border: 1px solid rgba(251,191,36,0.12);
    border-radius: 10px; padding: 0.7rem; margin-bottom: 0.5rem;
    font-size: 0.85rem; color: rgba(255,255,255,0.7); line-height: 1.5;
}
.assumption-row:last-child{margin-bottom:0;}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 12px !important; padding: 4px !important; gap: 3px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; border-radius: 9px !important;
    color: rgba(255,255,255,0.38) !important; font-weight: 600 !important;
    font-size: 0.82rem !important; padding: 0.5rem 1rem !important;
    border: none !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: rgba(255,255,255,0.7) !important;
    background: rgba(255,255,255,0.05) !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(99,102,241,0.18) !important;
    color: #a5b4fc !important; box-shadow: none !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding: 1.5rem 0 0 !important; background: transparent !important;
}
.stTabs [data-baseweb="tab-border"]{display:none !important;}

.agent-result {
    border-radius: 14px; padding: 1.75rem; border: 1px solid;
}
.agent-result-header {
    display: flex; align-items: center; gap: 12px;
    margin-bottom: 1.2rem; padding-bottom: 1.2rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.agent-result-icon {
    width: 42px; height: 42px; border-radius: 11px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem; flex-shrink: 0;
}
.agent-result-title { font-size: 1rem; font-weight: 700; color: #f1f5f9; }
.agent-result-desc {
    font-size: 0.75rem; color: #64748b; margin-top: 2px;
}
.agent-result-body {
    font-size: 0.9rem; color: rgba(255,255,255,0.78);
    line-height: 1.85; white-space: pre-wrap;
}

/* Divider override */
hr { border-color: rgba(255,255,255,0.06) !important; }

/* Error */
.alert-error {
    background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.25);
    border-radius: 10px; padding: 0.85rem 1.2rem; color: #fca5a5;
    font-size: 0.85rem; display: flex; align-items: center; gap: 8px;
    margin-bottom: 1rem;
}

/* Scrollbar */
::-webkit-scrollbar{width:5px;}
::-webkit-scrollbar-track{background:transparent;}
::-webkit-scrollbar-thumb{background:rgba(139,92,246,0.3);border-radius:3px;}

/* Subheader override for "Recent Debates" */
.stSubheader {
    color: #f1f5f9 !important;
}
</style>
""", unsafe_allow_html=True)


# SIDEBAR
with st.sidebar:
    st.markdown('<p class="sb-title">Active Agents</p>', unsafe_allow_html=True)
    agents_cfg = [
        ("🧠","#6366f1","Orchestrator",   "Manages debate flow"),
        ("☀️", "#facc15","Optimist",        "Champions the upside"),
        ("😈","#ef4444","Devil's Advocate","Challenges assumptions"),
        ("🛡️", "#f59e0b","Risk Analyst",    "Maps threats"),
        ("🔍","#3b82f6","Researcher",      "Grounds claims in data"),
        ("⚖️", "#a855f7","Judge",           "Delivers final verdict"),
    ]
    for icon, color, name, role in agents_cfg:
        st.markdown(f"""
        <div class="sb-agent">
            <div class="sb-agent-icon" style="background:{color}18;border:1px solid {color}30;">{icon}</div>
            <div>
                <div class="sb-agent-name">{name}</div>
                <div class="sb-agent-role">{role}</div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sb-title">Session Stats</p>', unsafe_allow_html=True)
    conf_display = f"{st.session_state.last_confidence}%" if st.session_state.last_confidence is not None else "—"
    st.markdown(f"""
    <div class="sb-stat-row">
        <div class="sb-stat">
            <div class="sb-stat-val">{st.session_state.debate_count}</div>
            <div class="sb-stat-lbl">Debates</div>
        </div>
        <div class="sb-stat">
            <div class="sb-stat-val">{conf_display}</div>
            <div class="sb-stat-lbl">Last Score</div>
        </div>
    </div>""", unsafe_allow_html=True)


# MAIN CONTENT
# ─ RESULTS VIEW
if st.session_state.show_results and st.session_state.result:
    result     = st.session_state.result
    verdict    = st.session_state.verdict
    confidence = verdict.get("confidence", 0)

    st.markdown(f"""
    <div class="results-header">
        <div class="results-title">Debate Results</div>
        <div class="results-meta">
            <span class="results-chip">6 agents consulted</span>
            <span class="results-chip">{st.session_state.debate_count} debate(s) run</span>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="verdict-banner">
        <div class="verdict-eyebrow">⚖️ Final Verdict</div>
        <div class="verdict-main">{verdict.get('verdict','No verdict returned.')}</div>
        <div class="verdict-conf-row">
            <span class="conf-label">AI Confidence</span>
            <div class="conf-track"><div class="conf-fill" style="width:{confidence}%;"></div></div>
            <span class="conf-pct">{confidence}%</span>
        </div>
    </div>""", unsafe_allow_html=True)

    factors    = verdict.get("factors", [])
    next_steps = verdict.get("next_steps", [])
    factors_html = "".join(
        f'<div class="info-item"><span class="info-marker" style="color:#818cf8;">◆</span><span>{f}</span></div>'
        for f in factors
    )
    steps_html = "".join(
        f'<div class="info-item"><span class="info-marker" style="color:#34d399;font-weight:700;min-width:16px;text-align:center;">{i+1}</span><span>{s}</span></div>'
        for i, s in enumerate(next_steps)
    )
    st.markdown(f"""
    <div class="info-grid">
        <div class="info-card">
            <div class="info-card-label" style="color:#818cf8;">🔑 Deciding Factors</div>
            {factors_html or '<span style="color:#475569;font-size:0.85rem;">None returned.</span>'}
        </div>
        <div class="info-card">
            <div class="info-card-label" style="color:#34d399;">🚀 Next Steps</div>
            {steps_html or '<span style="color:#475569;font-size:0.85rem;">None returned.</span>'}
        </div>
    </div>""", unsafe_allow_html=True)

    assumptions = verdict.get("assumptions", [])
    if assumptions:
        a_html = "".join(f'<div class="assumption-row"><span>⚠️</span><span>{a}</span></div>' for a in assumptions)
        st.markdown(f"""
        <div class="info-card" style="margin-bottom:1.25rem;">
            <div class="info-card-label" style="color:#fbbf24;">🧩 Critical Assumptions</div>
            {a_html}
        </div>""", unsafe_allow_html=True)

    tab_opt, tab_devil, tab_risk, tab_research = st.tabs([
        "😊 Optimist", "😈 Devil's Advocate", "🛡️ Risk Analysis", "🔍 Research"])
    tabs_cfg = [
        (tab_opt,"😊","#34d399","Optimist's Case","Strongest arguments in favour","optimist_case","rgba(52,211,153,0.05)","rgba(52,211,153,0.2)"),
        (tab_devil,"😈","#f87171","Devil's Advocate","Sharpest objections & worst cases","devil_case","rgba(248,113,113,0.05)","rgba(248,113,113,0.2)"),
        (tab_risk,"🛡️","#fbbf24","Risk Analysis","Threats, mitigations & probabilities","risk_assessment","rgba(251,191,36,0.05)","rgba(251,191,36,0.2)"),
        (tab_research,"🔍","#3b82f6","Research Evidence","Data, statistics & real-world cases","research_evidence","rgba(59,130,246,0.05)","rgba(59,130,246,0.2)"),
    ]
    for tab, icon, color, title, desc, key, bg, bc in tabs_cfg:
        with tab:
            st.markdown(f"""
            <div class="agent-result" style="background:{bg};border-color:{bc};">
                <div class="agent-result-header">
                    <div class="agent-result-icon" style="background:{color}18;border:1px solid {color}30;">{icon}</div>
                    <div><div class="agent-result-title">{title}</div><div class="agent-result-desc">{desc}</div></div>
                </div>
                <div class="agent-result-body">{result.get(key,'No content.')}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("↩ Start a New Debate", use_container_width=True):
        st.session_state.show_results = False
        st.session_state.result       = None
        st.session_state.verdict      = None
        st.session_state.decision_text = ""
        st.session_state.context_text  = ""
        st.rerun()


# ─ INPUT VIEW 
else:

    # ── 1. Hero 
    st.markdown("""
    <div class="hero">
        <div class="hero-badge">⚡ Powered by 6 AI Agents</div>
        <h1>Make Smarter Decisions<br>with <span>AI Debate</span></h1>
        <p class="hero-subtitle">
            Six AI agents argue every angle of your decision — optimist, critic,
            risk analyst, researcher, and more — then a judge delivers a
            confidence-scored verdict with actionable next steps.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── 2. Meet the Agents Showcase 
    showcase_agents = [
        ("🧠", "Orchestrator",  "Coordinates the multi-agent debate flow"),
        ("☀️",  "Optimist",     "Champions every upside and opportunity"),
        ("😈", "Devil's Advocate", "Stress-tests assumptions with tough questions"),
        ("🛡️", "Risk Analyst",  "Maps threats, mitigations & probabilities"),
        ("🔍", "Researcher",    "Grounds every claim in data & evidence"),
        ("⚖️",  "Judge",        "Weighs all arguments to reach a verdict"),
    ]
    cols = st.columns(6)
    for col, (emoji, name, role) in zip(cols, showcase_agents):
        with col:
            st.markdown(f"""
            <div class="agent-showcase-card">
                <span class="agent-showcase-emoji">{emoji}</span>
                <div class="agent-showcase-name">{name}</div>
                <div class="agent-showcase-role">{role}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")  # small spacer

    # ── 3. Main Form 
    with st.container():
        decision = st.text_area(
            "🎯 Your Decision",
            placeholder="e.g. Should I quit my job to start an AI consulting business?",
            height=100,
            key="decision_input",
            value=st.session_state.decision_text,
        )
        context = st.text_area(
            "📋 Additional Context (optional)",
            placeholder="e.g. I'm 28, have $50k in savings, 5 years experience...",
            height=80,
            key="context_input",
            value=st.session_state.context_text,
        )

    # ── 4. Advanced Settings Expander 
    with st.expander("⚙️ Advanced Settings", expanded=False):
        st.session_state.judge_harshness = st.slider(
            "Judge's Harshness Level",
            min_value=1, max_value=5,
            value=st.session_state.judge_harshness,
            help="1 = lenient  →  5 = extremely strict",
        )

        exc_cols = st.columns(2)
        with exc_cols[0]:
            st.session_state.exclude_optimist = st.checkbox(
                "Exclude ☀️ Optimist", value=st.session_state.exclude_optimist)
            st.session_state.exclude_risk = st.checkbox(
                "Exclude 🛡️ Risk Analyst", value=st.session_state.exclude_risk)
        with exc_cols[1]:
            st.session_state.exclude_devil = st.checkbox(
                "Exclude 😈 Devil's Advocate", value=st.session_state.exclude_devil)
            st.session_state.exclude_research = st.checkbox(
                "Exclude 🔍 Researcher", value=st.session_state.exclude_research)

    #Validation 
    if st.session_state.submitted and not decision.strip():
        st.markdown(
            '<div class="alert-error">⚠️ Please describe the decision you want debated.</div>',
            unsafe_allow_html=True,
        )
        st.session_state.submitted = False

    # ── 5. Primary CTA 
    launch = st.button("🚀  Start the Debate", type="primary", use_container_width=True)

    # Agent ticker 
    st.markdown("""
    <div style="text-align:center;margin-top:1rem;">
        <span style="font-size:0.7rem;color:#475569;">
            🧠 Orchestrator · ☀️ Optimist · 😈 Devil · 🛡️ Risk · 🔍 Researcher · ⚖️ Judge
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Debate Execution 
    if launch:
        if not decision.strip():
            st.session_state.submitted = True
            st.rerun()
        else:
            stages = [
                ("🧠","Orchestrator","Framing the debate…"),
                ("☀️", "Optimist",   "Building the case for…"),
                ("😈","Devil",       "Probing weaknesses…"),
                ("🛡️","Risk Analyst","Mapping threats…"),
                ("🔍","Researcher",  "Gathering evidence…"),
                ("⚖️", "Judge",      "Deliberating verdict…"),
            ]
            progress_ph   = st.empty()
            result_holder = {}
            error_holder  = {}

            def run_debate():
                try:
                    result_holder["data"] = run_decision_debate(decision, context)
                except Exception as exc:
                    error_holder["msg"] = str(exc)

            thread = threading.Thread(target=run_debate, daemon=True)
            thread.start()

            stage_idx = 0
            while thread.is_alive():
                si = stage_idx % len(stages)
                icon, _, action = stages[si]
                dots = "".join(
                    f'<span class="progress-dot {"done" if i<si else "active" if i==si else ""}"></span>'
                    for i in range(len(stages)))
                chips = "".join(
                    f'<span class="progress-agent-chip {"done" if i<si else "active" if i==si else ""}">{ic} {nm}</span>'
                    for i,(ic,nm,_) in enumerate(stages))
                progress_ph.markdown(f"""
                <div class="progress-wrap">
                    <span class="progress-stage-icon">{icon}</span>
                    <div class="progress-stage-title">{action}</div>
                    <div class="progress-stage-sub">~30 seconds · Agent {si+1} of {len(stages)}</div>
                    <div class="progress-dots">{dots}</div>
                    <div class="progress-agent-list">{chips}</div>
                </div>""", unsafe_allow_html=True)
                stage_idx += 1
                time.sleep(3)

            thread.join()
            progress_ph.empty()

            if error_holder:
                st.markdown(f'<div class="alert-error">⚠️ {error_holder["msg"]}</div>', unsafe_allow_html=True)
            else:
                result     = result_holder["data"]
                verdict    = json.loads(result["final_verdict"])
                confidence = verdict.get("confidence", 0)
                st.session_state.result          = result
                st.session_state.verdict         = verdict
                st.session_state.show_results    = True
                st.session_state.debate_count   += 1
                st.session_state.last_confidence = confidence
                st.rerun()

    # ── 6. Recent Debates Mock Section 
    st.markdown('<hr style="margin:2.5rem 0 2rem;border-color:rgba(255,255,255,0.06);">', unsafe_allow_html=True)
    st.subheader("📌 Explore Recent Debates")

    recent = [
        {
            "title": "Should we move to a 4-day work week?",
            "body":  "The team debated productivity, employee retention, and client impact. The judge ruled strongly in favour with a clear implementation roadmap.",
            "score": "92%", "pill_cls": "",
        },
        {
            "title": "Is it time to switch from AWS to GCP?",
            "body":  "Cost analysis, migration complexity, and team expertise were weighed. The verdict: stay on AWS but begin a phased PoC with GCP.",
            "score": "67%", "pill_cls": " amber",
        },
        {
            "title": "Should I pursue an MBA or keep working?",
            "body":  "ROI, opportunity cost, and career trajectory were debated extensively. The judge recommended deferring for 2 years to build savings first.",
            "score": "45%", "pill_cls": " red",
        },
    ]
    rc_cols = st.columns(3)
    for col, card in zip(rc_cols, recent):
        with col:
            st.markdown(f"""
            <div class="recent-card">
                <div class="recent-card-title">{card["title"]}</div>
                <div class="recent-card-body">{card["body"]}</div>
                <div><span class="conf-pill{card["pill_cls"]}">{card["score"]} Confidence</span></div>
            </div>
            """, unsafe_allow_html=True)