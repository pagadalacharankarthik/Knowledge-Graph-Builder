# PRODUCTION_VERSION: 4.5.2 (LATEST)
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from rag import answer_question, load_vector_db
from graph import get_top_persons, get_graph_data_for_visualization

# Setup UI page configuration
st.set_page_config(
    page_title="Enterprise Intelligence Hub",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Compact Control Center UI
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 0rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 100% !important;
        }
        .main {
            background-color: #0b0e14;
            color: #d1d5db;
        }
        [data-testid="stHeader"] { background: rgba(0,0,0,0); }
        
        .control-pane {
            background: rgba(22, 28, 38, 0.7);
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 1rem;
        }
        .stMetric {
            background: transparent !important;
            padding: 0 !important;
        }
        .stMetric [data-testid="stMetricValue"] {
            color: #38bdf8 !important;
            font-size: 1.8rem !important;
        }
        .stButton button {
            background: #38bdf8;
            color: #000;
            font-weight: 700;
            border-radius: 6px;
            width: 100%;
            height: 42px;
            border: none;
        }
        .answer-area {
            background: rgba(56, 189, 248, 0.05);
            border-left: 3px solid #38bdf8;
            padding: 15px;
            border-radius: 4px;
            font-size: 0.95rem;
            margin-top: 10px;
        }
        .footer-pin {
            position: fixed;
            bottom: 10px;
            right: 20px;
            font-size: 0.85rem;
            color: #38bdf8;
            font-weight: 900;
            letter-spacing: 1px;
            text-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
            z-index: 100;
        }
        /* Tab height optimization */
        .stTabs [data-baseweb="tab-panel"] {
            max-height: 200px;
            overflow-y: auto;
        }
    </style>
""", unsafe_allow_html=True)

# Optimized Caching for Speed
@st.cache_resource(show_spinner="🛡️ Initializing Enterprise Intel Core...")
def initialize_intelligence_engine():
    # Force a deep reload of the RAG backend
    import rag
    import importlib
    importlib.reload(rag)
    success = rag.load_vector_db()
    return success

# Main Resources Injection
db_ready = initialize_intelligence_engine()

# Grid Layout
left_pane, mid_pane, right_pane = st.columns([0.8, 1.5, 1.5], gap="medium")

# 1. ANALYTICS PANE
with left_pane:
    st.markdown('<div class="control-pane">', unsafe_allow_html=True)
    st.markdown("#### 📊 ARCHIVE STATUS")
    ma, mb = st.columns(2)
    with ma: st.metric("CORPUS", "10K")
    with mb: st.metric("NODES", "5K+")
    
    st.markdown("<br>#### 🏆 TOP ENTITIES", unsafe_allow_html=True)
    leaders = get_top_persons(limit=7)
    if leaders:
        for l in leaders:
            st.markdown(f"<div style='font-size:0.85rem; margin-bottom:6px;'>{l['name'].title()} <span style='float:right; color:#38bdf8;'>{l['connections']}</span></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 REBOOT SYSTEM"):
        st.cache_resource.clear()
        st.session_state.clear()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 2. DISCOVERY PANE
with mid_pane:
    st.markdown('<div class="control-pane">', unsafe_allow_html=True)
    st.markdown("#### 🔍 CONTEXTUAL SEARCH")
    query = st.text_input("QUERY_INPUT", placeholder="Request analysis...", label_visibility="collapsed")
    if st.button("EXECUTE"):
        if query:
            if db_ready:
                with st.spinner("Synthesizing..."):
                    res = answer_question(query)
                    st.markdown("#### 💡 SYSTEM RESPONSE (JSON)")
                    
                    # Dynamic Diagnosis info (Busts the 'Empty Data' mystery)
                    db_rows = res.get('db_rows', 0)
                    st.sidebar.markdown(f"**Intelligence Core Status:** {'🟢 ACTIVE' if db_rows > 0 else '🔴 EMPTY'}")
                    st.sidebar.write(f"Total Mails: {db_rows:,}")

                    # Display the exact fields the user expects from Milestone 3
                    output_display = {
                        "question": res.get("question", query),
                        "answer": res.get("answer"),
                        "extracted_entities": res.get("extracted_entities", []),
                        "retrieval_latency_seconds": res.get("retrieval_latency_seconds", 0.0)
                    }
                    st.json(output_display)
                    
                    with st.expander("🛠️ NEURAL TRACE (Vector + Graph Verification)"):
                        st.markdown("**Semantically Retrieved from FAISS Vector DB:**")
                        for idx, email in enumerate(res.get('retrieved_emails', [])):
                            st.info(f"Email {idx+1}: {email[:200]}...")
                        
                        st.markdown("**Retrieved from Neo4j Knowledge Graph:**")
                        if res.get('retrieved_graph'):
                            st.success("\n".join(res['retrieved_graph']))
                        else:
                            st.warning("No direct graph relationships found for this specific entity.")

                    t1, t2 = st.tabs(["📧 FULL CONTEXT", "🕸️ GRAPH VIEW"])
                    with t1:
                        if res.get('retrieved_emails'):
                            for e in res['retrieved_emails'][:3]:
                                st.markdown(f"<div style='font-size:0.8rem; opacity:0.7; padding:8px; border-bottom:1px solid #1e293b;'>{e[:400]}...</div>", unsafe_allow_html=True)
                    with t2:
                        if res.get('retrieved_graph'):
                            st.code("\n".join(res['retrieved_graph']), language="text")
            else:
                st.error("System Initialization Failed. Click Reboot.")
    else:
        st.info("System Ready. Enter parameters.")
    st.markdown('</div>', unsafe_allow_html=True)

# 3. VISUALIZATION PANE
with right_pane:
    st.markdown('<div class="control-pane">', unsafe_allow_html=True)
    st.markdown("#### 🕸️ TOPOLOGY OVERVIEW")
    nodes, edges = get_graph_data_for_visualization(limit=40)
    if nodes:
        net = Network(height="460px", width="100%", bgcolor="transparent", font_color="#d1d5db")
        net.force_atlas_2based()
        for n, l in nodes:
            net.add_node(n, label=n, color="#38bdf8" if l == "PERSON" else "#818cf8")
        for s, t in edges:
            net.add_edge(s, t, color="#1e293b")
        
        path = os.path.join(os.path.dirname(__file__), "temp_graph.html")
        net.save_graph(path)
        with open(path, "r", encoding="utf-8") as f:
            html_data = f.read()
        components.html(html_data, height=480)
    else:
        st.warning("Awaiting Graph Node Load")
    st.markdown('</div>', unsafe_allow_html=True)

# Fixed Branding
st.markdown("<div class='footer-pin'>BUILD BY CHARAN KARTHIK</div>", unsafe_allow_html=True)
