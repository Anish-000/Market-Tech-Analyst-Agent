import streamlit as st
import sys
import os
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph.pipeline import build_pipeline, get_initial_state

st.set_page_config(
    page_title="Market & Tech Analyst Agent",
    page_icon="◈",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background-color: #0a0a0f;
    color: #e8e6e0;
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background: #0a0a0f;
    background-image:
        radial-gradient(ellipse 80% 50% at 20% 10%, rgba(99, 76, 230, 0.08) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(230, 76, 99, 0.06) 0%, transparent 60%);
}

[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { display: none; }

section[data-testid="stMain"] > div { padding: 2rem 3rem; }

/* ── HEADER ── */
.header-wrap {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 2.5rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid rgba(255,255,255,0.07);
}
.header-left { display: flex; flex-direction: column; gap: 0.4rem; }
.header-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    font-weight: 400;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #7c6ee0;
}
.header-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.6rem;
    font-weight: 800;
    line-height: 1.2;
    color: #f0ede8;
    letter-spacing: -0.02em;
    padding-bottom: 0.2rem
}
.header-title span { color: #7c6ee0; }
.header-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(99, 76, 230, 0.12);
    border: 1px solid rgba(99, 76, 230, 0.25);
    border-radius: 20px;
    padding: 0.3rem 0.85rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    color: #9d8ff0;
    letter-spacing: 0.05em;
    margin-top: 0.5rem;
    width: fit-content;
}
.badge-dot {
    width: 6px; height: 6px;
    background: #7c6ee0;
    border-radius: 50%;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.8); }
}

/* ── SECTION LABELS ── */
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #5a5670;
    margin-bottom: 0.75rem;
}

/* ── INPUT AREA ── */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #e8e6e0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.85rem 1.1rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(124, 110, 224, 0.5) !important;
    box-shadow: 0 0 0 3px rgba(124, 110, 224, 0.08) !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder { color: #3d3a50 !important; }

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #7c6ee0 0%, #5b4fd4 100%) !important;
    border: none !important;
    border-radius: 10px !important;
    color: #fff !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.03em !important;
    padding: 0.75rem 1.5rem !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
    box-shadow: 0 4px 20px rgba(124, 110, 224, 0.25) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 28px rgba(124, 110, 224, 0.35) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── DOWNLOAD BUTTON ── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #2a9d6e 0%, #1f7a54 100%) !important;
    border: none !important;
    border-radius: 10px !important;
    color: #fff !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 0.75rem 1.5rem !important;
    box-shadow: 0 4px 20px rgba(42, 157, 110, 0.25) !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
}
.stDownloadButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 28px rgba(42, 157, 110, 0.35) !important;
}

/* ── SOURCE CARDS ── */
.source-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.6rem;
    transition: border-color 0.2s, background 0.2s;
}
.source-card:hover {
    border-color: rgba(124, 110, 224, 0.3);
    background: rgba(124, 110, 224, 0.04);
}
.source-title {
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    font-size: 0.88rem;
    color: #e0ddf5;
    margin-bottom: 0.25rem;
}
.source-url {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    color: #7c6ee0;
    margin-bottom: 0.3rem;
    word-break: break-all;
}
.source-preview {
    font-size: 0.78rem;
    color: #5a5670;
    line-height: 1.5;
}

/* ── CHECKBOXES ── */

.stCheckbox > label > span:first-child {
    background-color: #7c6ee0 !important;
    border-color: #7c6ee0 !important;
}
[data-testid="stCheckbox"] input:checked + div {
    background-color: #7c6ee0 !important;
    border-color: #7c6ee0 !important;
}
[data-testid="stCheckbox"] svg {
    fill: #ffffff !important;
    color: #ffffff !important;
}

/* ── LOG PANEL ── */
.log-panel {
    background: rgba(10, 8, 20, 0.8);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 1.2rem;
    height: 520px;
    overflow-y: auto;
    font-family: 'DM Mono', monospace;
}
.log-panel::-webkit-scrollbar { width: 4px; }
.log-panel::-webkit-scrollbar-track { background: transparent; }
.log-panel::-webkit-scrollbar-thumb { background: rgba(124,110,224,0.3); border-radius: 2px; }
.log-entry {
    display: flex;
    gap: 0.6rem;
    align-items: flex-start;
    padding: 0.35rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.03);
    font-size: 0.72rem;
    line-height: 1.5;
}
.log-time { color: #3d3a50; white-space: nowrap; flex-shrink: 0; }
.log-icon { flex-shrink: 0; }
.log-text-researcher { color: #7c6ee0; }
.log-text-analyst { color: #e0943a; }
.log-text-writer { color: #2a9d6e; }
.log-text-system { color: #8a8699; }
.log-text-user { color: #e06e7c; }
.log-empty { color: #2a2840; font-size: 0.72rem; text-align: center; padding-top: 2rem; }

/* ── ANALYSIS RESULT ── */

.analysis-heading {
    font-family: 'Syne', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #c4b8f5;
    letter-spacing: 0.04em;
    margin: 1.5rem 0 0.6rem;
    padding-left: 0.75rem;
    border-left: 3px solid #7c6ee0;
}
            
.analysis-wrap {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 1.8rem 2rem;
    margin-top: 1rem;
}
.analysis-wrap h1, .analysis-wrap h2, .analysis-wrap h3 {
    font-family: 'Syne', sans-serif !important;
    color: #f0ede8 !important;
    margin: 1.2rem 0 0.6rem !important;
}
.analysis-wrap p, .analysis-wrap li {
    color: #b8b4cc !important;
    font-size: 0.92rem !important;
    line-height: 1.75 !important;
}
.analysis-wrap strong { color: #e0ddf5 !important; }

/* ── CITATIONS ── */
.citation-item {
    display: flex;
    gap: 0.75rem;
    align-items: flex-start;
    padding: 0.65rem 0.9rem;
    border-radius: 8px;
    margin-bottom: 0.4rem;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    transition: border-color 0.2s;
    text-decoration: none;
}
.citation-item:hover { border-color: rgba(124,110,224,0.3); }
.citation-num {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    color: #7c6ee0;
    background: rgba(124,110,224,0.1);
    border-radius: 4px;
    padding: 0.1rem 0.4rem;
    flex-shrink: 0;
    margin-top: 0.1rem;
}
.citation-title { font-size: 0.83rem; color: #c8c4e0; font-weight: 500; }
.citation-url { font-family: 'DM Mono', monospace; font-size: 0.65rem; color: #5a5670; margin-top: 0.15rem; }

/* ── SUCCESS BANNER ── */
.success-banner {
    background: linear-gradient(135deg, rgba(42,157,110,0.12) 0%, rgba(42,157,110,0.05) 100%);
    border: 1px solid rgba(42,157,110,0.25);
    border-radius: 10px;
    padding: 0.9rem 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
    font-size: 0.88rem;
    color: #5ecba1;
    font-family: 'DM Sans', sans-serif;
}

/* ── INFO BANNER ── */
.info-banner {
    background: rgba(124, 110, 224, 0.07);
    border: 1px solid rgba(124, 110, 224, 0.2);
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-size: 0.82rem;
    color: #9d8ff0;
    font-family: 'DM Mono', monospace;
    margin-bottom: 1rem;
}

/* ── SELECTION COUNTER ── */
.selection-counter {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: #7c6ee0;
    background: rgba(124,110,224,0.08);
    border: 1px solid rgba(124,110,224,0.2);
    border-radius: 6px;
    padding: 0.35rem 0.75rem;
    display: inline-block;
    margin: 0.75rem 0 1rem;
}

/* ── DIVIDER ── */
.styled-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(124,110,224,0.3), transparent);
    margin: 2rem 0;
}

/* ── HIDE STREAMLIT DEFAULTS ── */
#MainMenu, footer, [data-testid="stToolbar"] { display: none !important; }
.block-container { padding-top: 2rem !important; max-width: 100% !important; }
[data-testid="stVerticalBlock"] > div { gap: 0.5rem; }
</style>
""", unsafe_allow_html=True)


# ── SESSION STATE ──
if "pipeline_state" not in st.session_state:
    st.session_state.pipeline_state = None
if "pipeline" not in st.session_state:
    st.session_state.pipeline = None
if "stage" not in st.session_state:
    st.session_state.stage = "input"
if "logs" not in st.session_state:
    st.session_state.logs = []


def add_log(message: str, agent: str = "system"):
    from datetime import datetime
    st.session_state.logs.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "text": message,
        "agent": agent
    })


def render_log_panel():
    icons = {
        "researcher": "◈",
        "analyst": "◆",
        "writer": "◉",
        "system": "·",
        "user": "▸"
    }
    if not st.session_state.logs:
        st.markdown('<div class="log-panel"><div class="log-empty">— awaiting activity —</div></div>', unsafe_allow_html=True)
    else:
        entries_html = ""
        for log in st.session_state.logs:
            agent = log.get("agent", "system")
            icon = icons.get(agent, "·")
            entries_html += f"""
            <div class="log-entry">
                <span class="log-time">{log['time']}</span>
                <span class="log-icon log-text-{agent}">{icon}</span>
                <span class="log-text-{agent}">{log['text']}</span>
            </div>"""
        st.markdown(f'<div class="log-panel">{entries_html}</div>', unsafe_allow_html=True)


# ── HEADER ──
st.markdown("""
<div class="header-wrap">
    <div class="header-left">
        <span class="header-eyebrow">Autonomous Research System</span>
        <div class="header-title">Market & Tech<br><span>Analyst Agent</span></div>
        <div class="header-badge">
            <span class="badge-dot"></span>
            3-Agent Pipeline · ChromaDB Memory · Human-in-Loop
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── LAYOUT ──
left_col, right_col = st.columns([2, 1], gap="large")

with right_col:
    st.markdown('<div class="section-label">Agent Activity Log</div>', unsafe_allow_html=True)
    render_log_panel()


# ══════════════════════════════════════
# STAGE 1 — QUERY INPUT
# ══════════════════════════════════════
with left_col:
    if st.session_state.stage == "input":
        st.markdown('<div class="section-label">Research Query</div>', unsafe_allow_html=True)

        query = st.text_input(
            label="query",
            placeholder="e.g. Compare Nvidia RTX 5090 vs AMD RX 9070 for deep learning",
            label_visibility="collapsed"
        )

        if st.button("Launch Research Pipeline", use_container_width=True):
            if query.strip() == "":
                st.warning("Please enter a research topic.")
            else:
                with st.spinner("Agent 1 (Researcher) is searching the web..."):
                    add_log(f"Query received: '{query}'", "user")
                    add_log("Building agent pipeline...", "system")
                    add_log("Checking ChromaDB memory for past research...", "researcher")

                    pipeline = build_pipeline()
                    initial_state = get_initial_state(query)
                    result_state = pipeline.invoke(initial_state)

                    st.session_state.pipeline = pipeline
                    st.session_state.pipeline_state = result_state
                    st.session_state.stage = "source_selection"

                    add_log(f"Web search complete — {len(result_state['search_results'])} sources found.", "researcher")
                    add_log("Waiting for source selection...", "system")
                st.rerun()


    # ══════════════════════════════════════
    # STAGE 2 — SOURCE SELECTION
    # ══════════════════════════════════════
    elif st.session_state.stage == "source_selection":
        search_results = st.session_state.pipeline_state.get("search_results", [])
        past_research = st.session_state.pipeline_state.get("past_research", [])

        st.markdown('<div class="section-label">Human-in-the-Loop · Source Selection</div>', unsafe_allow_html=True)
        st.markdown("""
            <div style="font-family: 'DM Sans', sans-serif; font-size: 0.92rem; color: #8a8699; margin-bottom: 1.2rem; line-height: 1.6;">
                The Researcher Agent found the sources below. Select <strong style="color:#e0ddf5">3 sources</strong> to focus the analysis on.
            </div>
        """, unsafe_allow_html=True)

        if past_research:
            st.markdown(f'<div class="info-banner">◈ Memory — {len(past_research)} past research entries found for this topic. They will be included automatically.</div>', unsafe_allow_html=True)

        selected = []
        for i, source in enumerate(search_results):
            col1, col2 = st.columns([0.04, 0.96])
            with col1:
                checked = st.checkbox("", key=f"source_{i}", label_visibility="collapsed")
            with col2:
                st.markdown(f"""
                    <div class="source-card">
                        <div class="source-title">{source['title']}</div>
                        <div class="source-url">{source['url']}</div>
                        <div class="source-preview">{source['content'][:130]}...</div>
                    </div>
                """, unsafe_allow_html=True)
            if checked:
                selected.append(i)

        st.markdown(f'<div class="selection-counter">▸ {len(selected)} source{"s" if len(selected) != 1 else ""} selected</div>', unsafe_allow_html=True)

        if st.button("Confirm Selection & Run Analysis", use_container_width=True):
            if len(selected) == 0:
                st.warning("Please select at least one source.")
            else:
                with st.spinner("Agents are working... this may take 30-60 seconds."):
                    add_log(f"User selected {len(selected)} sources.", "user")
                    add_log("Scraping selected pages...", "researcher")

                    st.session_state.pipeline_state["selected_indices"] = selected
                    st.session_state.pipeline_state["awaiting_source_selection"] = False

                    from agents.researcher import researcher_agent_after_selection
                    from agents.analyst import analyst_agent
                    from agents.writer import writer_agent

                    state = researcher_agent_after_selection(st.session_state.pipeline_state)
                    add_log("Pages scraped. Raw research collected.", "researcher")
                    add_log("Passing data to Analyst Agent...", "system")

                    state = analyst_agent(state)
                    add_log("Price-to-performance analysis complete.", "analyst")
                    add_log("Trends and patterns identified.", "analyst")
                    add_log("Passing to Writer Agent...", "system")

                    state = writer_agent(state)
                    add_log("PDF report compiled and saved.", "writer")
                    add_log("Pipeline complete.", "system")

                    st.session_state.pipeline_state = state
                    st.session_state.stage = "results"
                st.rerun()


    # ══════════════════════════════════════
    # STAGE 3 — RESULTS
    # ══════════════════════════════════════
    elif st.session_state.stage == "results":
        state = st.session_state.pipeline_state
        analysis = state.get("analysis", "")
        pdf_path = state.get("pdf_path", "")
        selected_sources = state.get("selected_sources", [])

        st.markdown("""
            <div class="success-banner">
                ✦ &nbsp; All three agents completed successfully. Your report is ready.
            </div>
        """, unsafe_allow_html=True)

        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="Download PDF Report",
                    data=f,
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf",
                    use_container_width=True
                )

        st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Analysis Summary</div>', unsafe_allow_html=True)

        def format_analysis(text):
            lines = text.split("\n")
            formatted = []
            for line in lines:
                line = line.strip()
                clean = line.lstrip("#").strip()
                if line.startswith("#") or (len(clean) > 0 and clean == clean.upper() and len(clean) > 5):
                    formatted.append(f'<div class="analysis-heading">{clean}</div>')
                else:
                    formatted.append(line)
            return "\n".join(formatted)
        cleaned_analysis = format_analysis(analysis)
        st.markdown(f'<div class="analysis-wrap">{cleaned_analysis}</div>', unsafe_allow_html=True)

        if selected_sources:
            st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)
            st.markdown('<div class="section-label">Sources & Citations</div>', unsafe_allow_html=True)
            for i, source in enumerate(selected_sources):
                title = source.get("title", "Unknown Source")
                url = source.get("url", "")
                st.markdown(f"""
                    <a href="{url}" target="_blank" class="citation-item">
                        <span class="citation-num">{i+1:02d}</span>
                        <div>
                            <div class="citation-title">{title}</div>
                            <div class="citation-url">{url}</div>
                        </div>
                    </a>
                """, unsafe_allow_html=True)

        st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)

        if st.button("Start New Research", use_container_width=True):
            st.session_state.pipeline_state = None
            st.session_state.pipeline = None
            st.session_state.stage = "input"
            st.session_state.logs = []
            st.rerun()