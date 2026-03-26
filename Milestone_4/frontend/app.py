import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
import os
import sys

# Add backend to path to allow importing modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from rag import answer_question, load_vector_db
from graph import get_top_persons, get_graph_data_for_visualization

# Setup UI page configuration
st.set_page_config(
    page_title="AI Knowledge Graph Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium CSS Injection
st.markdown("""
    <style>
        .main {
            background-color: #0f111a;
            color: #e2e8f0;
            font-family: 'Inter', sans-serif;
        }
        h1, h2, h3 {
            color: #f8fafc;
            font-weight: 700;
        }
        h1 {
            background: -webkit-linear-gradient(45deg, #3b82f6, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem !important;
            padding-bottom: 20px;
        }
        .stButton button {
            background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
            color: white;
            border-radius: 8px;
            border: none;
            padding: 0.5rem 1.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .stButton button:hover {
            box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4);
            transform: translateY(-2px);
        }
        .stTextInput input, .stTextArea textarea {
            background-color: #1e2130 !important;
            color: white !important;
            border: 1px solid #3b82f6 !important;
            border-radius: 8px;
        }
        .metric-card {
            background: rgba(30, 33, 48, 0.6);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
            margin-bottom: 1rem;
        }
        .answer-box {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
            border-left: 4px solid #8b5cf6;
            padding: 1.5rem;
            border-radius: 8px;
            font-size: 1.1rem;
            line-height: 1.6;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Main Title
st.markdown("<h1>🧠 AI Knowledge Graph Dashboard</h1>", unsafe_allow_html=True)
st.markdown("Query the Enron dataset through an advanced Retrieval-Augmented Generation (RAG) and Neo4j Knowledge Graph syste# Compact Glassmorphism UI (Dark Control Center)
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 0rem !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
            max-width: 100% !important;
        }
        .main {
            background-color: #0c0f16;
            color: #e2e8f0;
            overflow: hidden;
        }
        [data-testid="stSidebar"] {
            background-color: #141b26;
            border-right: 1px solid #1e293b;
        }
        .compact-card {
            background: rgba(20, 27, 38, 0.6);
            border: 1px solid #1e293b;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 10px;
        }
        .stMetric {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
        }
        .stMetric [data-testid="stMetricValue"] {
            font-size: 1.4rem !important;
            color: #38bdf8 !important;
        }
        .stMetric [data-testid="stMetricLabel"] {
            font-size: 0.8rem !important;
            opacity: 0.7;
        }
        .stButton button {
            background: #38bdf8;
            color: #000;
            font-weight: 700;
            border-radius: 4px;
            height: 38px;
        }
        .footer-compact {
            position: fixed;
            bottom: 5px;
            right: 15px;
            font-size: 0.8rem;
            color: #38bdf8;
            font-weight: 800;
            letter-spacing: 1px;
            z-index: 99;
        }
        /* Custom Scrollbars for small containers */
        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 4px; }
        
        /* Ensure specific containers don't cause page scroll */
        .stTabs [data-baseweb="tab-panel"] {
            max-height: 250px;
            overflow-y: auto;
        }
    </style>
""", unsafe_allow_html=True)

# Compact Header
h_col1, h_col2 = st.columns([3, 1])
with h_col1:
    st.markdown("<h2 style='margin-bottom:0;'>🛡️ INTELLIGENCE HUB</h2>", unsafe_allow_html=True)
with h_col2:
    st.markdown("<div style='text-align:right; padding-top:10px; opacity:0.6; font-size:0.8em;'>V2.0 STABLE</div>", unsafe_allow_html=True)

# Main Control Panes
c1, c2, c3 = st.columns([0.8, 1.4, 1.4], gap="small")

# Pane 1: Analytics & Leaders (Left)
with c1:
    st.markdown('<div class="compact-card">', unsafe_allow_html=True)
    st.markdown("##### 📊 ANALYTICS")
    aa, bb = st.columns(2)
    with aa: st.metric("CORPUS", "10K")
    with bb: st.metric("ENTITIES", "5K+")
    st.markdown("---")
    st.markdown("##### 🏆 TOP NODES")
    top_p = get_top_persons(limit=6)
    if top_p:
        for p in top_p:
            st.markdown(f"<div style='font-size:0.8rem;'>{p['name'].title()} <span style='color:#38bdf8; float:right;'>{p['connections']}</span></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Pane 2: Query & Synthesis (Middle)
with c2:
    st.markdown('<div class="compact-card">', unsafe_allow_html=True)
    st.markdown("##### 🔍 SEARCH")
    query = st.text_input("", placeholder="Enter inquiry...", label_visibility="collapsed")
    run = st.button("ANALYSIS")
    
    if run and query:
        with st.spinner("Processing..."):
            res = answer_question(query)
            st.markdown("##### 💡 SYNTHESIS")
            st.markdown(f"<div style='background:rgba(56,189,248,0.1); padding:10px; border-radius:4px; font-size:0.9rem; line-height:1.4; border-left:2px solid #38bdf8;'>{res['answer']}</div>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            t1, t2 = st.tabs(["📧 DOCS", "🕸️ GRAPH"])
            with t1:
                if res['retrieved_emails']:
                    for e in res['retrieved_emails'][:2]:
                        st.markdown(f"<div style='font-size:0.75rem; margin-bottom:5px; opacity:0.8;'>{e[:250]}...</div>", unsafe_allow_html=True)
                else: st.info("Zero hits.")
            with t2:
                if res['retrieved_graph']:
                    st.code("\n".join(res['retrieved_graph'][:4]), language="text")
    else:
        st.info("System idle. Awaiting instruction.")
    st.markdown('</div>', unsafe_allow_html=True)

# Pane 3: Topology (Right)
with c3:
    st.markdown('<div class="compact-card" style="height: 100%;">', unsafe_allow_html=True)
    st.markdown("##### 🕸️ TOPOLOGY")
    nodes, edges = get_graph_data_for_visualization(limit=35)
    if nodes:
        net = Network(height="480px", width="100%", bgcolor="transparent", font_color="#e2e8f0")
        net.force_atlas_2based()
        for node, lbl in nodes:
            net.add_node(node, label=node, color="#38bdf8" if lbl == "PERSON" else "#818cf8")
        for s, t in edges:
            net.add_edge(s, t, color="#1e293b")
        
        path = os.path.join(os.path.dirname(__file__), "temp_graph.html")
        net.save_graph(path)
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        components.html(html, height=490)
    else:
        st.warning("Topology ready.")
    st.markdown('</div>', unsafe_allow_html=True)

# Branding Footer (Locked to Corner)
st.markdown("<div class='footer-compact'>BUILD BY CHARAN KARTHIK</div>", unsafe_allow_html=True)

# Ensure session state for database
if 'db_loaded' not in st.session_state:
    st.session_state.db_loaded = load_vector_db()
 </div>
""", unsafe_allow_html=True)
