# PRODUCTION_VERSION: 4.5.2 (LATEST)
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
import os
import sys
import pandas as pd  # type: ignore

# Add backend to path (must be absolute for Streamlit Cloud)
_backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if _backend_path not in sys.path:
    sys.path.insert(0, _backend_path)

try:
    from rag import answer_question, get_email_stats  # type: ignore
    from graph import get_top_persons, get_graph_data_for_visualization, get_kpis, get_top_entities, get_most_connected_nodes  # type: ignore
    from metrics import load_metrics  # type: ignore
except ImportError as e:
    st.error(f"Backend Import Error: {e}. Backend path: {_backend_path}")
    st.stop()

# Setup UI page configuration
st.set_page_config(
    page_title="Enterprise Intelligence Hub",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Compact Control Center UI
st.markdown("""
    <style>
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 100% !important;
        }
        .main {
            background-color: #0b0e14;
            color: #d1d5db;
        }
        [data-testid="stHeader"] {
            background: rgba(0,0,0,0) !important;
            visibility: hidden !important;
            height: 0px !important;
            min-height: 0px !important;
        }
        [data-testid="stToolbar"] { display: none !important; }
        
        .control-pane {
            background: rgba(15, 23, 42, 0.85);
            border: 1.5px solid rgba(56, 189, 248, 0.25);
            border-radius: 14px;
            padding: 1.25rem;
            margin-bottom: 1rem;
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.07), inset 0 1px 0 rgba(255,255,255,0.04);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
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
        /* End CSS */
    </style>
""", unsafe_allow_html=True)

# Optimized Caching for Speed
@st.cache_resource(show_spinner="🛡️ Initializing Enterprise Intel Core...")
def initialize_knowledge_core():
    # Force a deep reload of the RAG backend
    import rag
    import importlib
    importlib.reload(rag)
    # The new class-based singleton init
    success = rag.KnowledgeCore.get_instance().load()
    return success

# Main Resources Injection
db_ready = initialize_knowledge_core()

# Topology Controls mapped below

# Tabbed Interface for Professional Layout
tab_intel, tab_analytics = st.tabs(["🔎 INTELLIGENCE HUB", "📈 ADVANCED ANALYTICS"])

with tab_intel:
    # Intelligence Hub: Vertical Pane Layout
    kpis = get_kpis()
    col_left, col_right = st.columns([1, 1], gap="medium")
    
    with col_left:
        # Box 1: KPI Summary
        st.markdown('<div class="control-pane">', unsafe_allow_html=True)
        st.markdown("#### 📧 ARCHIVE STATUS")
        k1, k2, k3 = st.columns(3)
        k1.metric("CORPUS", "10K")
        k2.metric("PEOPLE", kpis.get("persons", "0"))
        k3.metric("ORGS", kpis.get("orgs", "0"))
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Box 2: Search Core
        st.markdown('<div class="control-pane" style="min-height: 600px;">', unsafe_allow_html=True)
        st.markdown("#### 🔍 CONTEXTUAL SEARCH")
        query = st.text_input("QUERY_INPUT", placeholder="Request analysis...", label_visibility="collapsed")
        if st.button("EXECUTE SEARCH"):
            if query:
                if db_ready:
                    with st.spinner("Synthesizing..."):
                        res = answer_question(query)
                        st.markdown(f"""
                            <div class="answer-area">
                                <h4 style='margin:0; color:#38bdf8;'>💡 SYSTEM RESPONSE</h4>
                                <p style='margin-top:10px;'>{res.get('answer')}</p>
                                <span style='font-size:0.8rem; opacity:0.6;'>Latency: {res.get('retrieval_latency_seconds', 0.0):.2f}s | Entities: {len(res.get('extracted_entities', []))}</span>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        with st.expander("🛠️ NEURAL TRACE (Vector + Graph Audit)", expanded=True):
                            for idx, email in enumerate(res.get('retrieved_emails', [])):
                                st.info(f"REFERENCE {idx+1}: {email[:200]}...")
                            if res.get('retrieved_graph'):
                                st.success("\n".join(res['retrieved_graph']))
        else:
            st.info("AI Core Standby. Enter query.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        # Box 3: Topology Summary
        st.markdown('<div class="control-pane">', unsafe_allow_html=True)
        st.markdown("#### 🕸️ TOPOLOGY STATUS")
        k4, k5, k6 = st.columns(3)
        k4.metric("NODES", kpis.get("nodes", "0"))
        k5.metric("EDGES", kpis.get("edges", "0"))
        k6.metric("LOCS", kpis.get("locations", "0"))
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Box 4: Topology Viewer
        st.markdown('<div class="control-pane" style="min-height: 600px;">', unsafe_allow_html=True)
        st.markdown("#### 🕸️ TOPOLOGY OVERVIEW")
        g1, g2 = st.columns(2)
        with g1: node_limit = st.slider("Node Density", 10, 500, 150)
        with g2: entity_filter = st.selectbox("Entity Type", ["ALL", "PERSON", "ORG", "LOCATION"])
        
        nodes, edges = get_graph_data_for_visualization(limit=node_limit, filter_label=entity_filter)
        if nodes:
            top_node = get_most_connected_nodes(limit=1)
            top_name = top_node[0]['name'] if top_node else None
            net = Network(height="450px", width="100%", bgcolor="transparent", font_color="#38bdf8")
            net.force_atlas_2based()
            colors = {"PERSON": "#38bdf8", "ORG": "#818cf8", "LOCATION": "#34d399"}
            for n, l in nodes:
                net.add_node(n, label=n, color=colors.get(l, "#f472b6"), size=30 if n == top_name else 15)
            for s, t in edges: net.add_edge(s, t, color="rgba(56, 189, 248, 0.1)")
            
            path = os.path.join(os.path.dirname(__file__), "temp_graph_intel.html")
            net.save_graph(path)
            with open(path, "r", encoding="utf-8") as f: components.html(f.read(), height=480)
        st.markdown('</div>', unsafe_allow_html=True)

with tab_analytics:
    # 1. ENTITY & DATA INSIGHTS
    st.markdown("### 📊 DATASET & NETWORK INSIGHTS")
    a1, a2 = st.columns(2)
    
    with a1:
        st.markdown('<div class="control-pane">', unsafe_allow_html=True)
        st.markdown("#### 🏆 TOP ENTITIES (MENTIONS)")
        at1, at2 = st.tabs(["PEOPLE", "ORGANIZATIONS"])
        with at1:
            p_data = get_top_entities("PERSON", 10)
            if p_data: st.bar_chart(pd.DataFrame(p_data).set_index('name')['connections'])
        with at2:
            o_data = get_top_entities("ORG", 10)
            if o_data: st.bar_chart(pd.DataFrame(o_data).set_index('name')['connections'])
        st.markdown('</div>', unsafe_allow_html=True)

    with a2:
        st.markdown('<div class="control-pane">', unsafe_allow_html=True)
        st.markdown("#### 🕸️ NETWORK CENTRALITY")
        central_nodes = get_most_connected_nodes(10)
        if central_nodes: st.table(pd.DataFrame(central_nodes))
        
        st.markdown("#### 📧 EMAIL LENGTH DISTRIBUTION")
        estats = get_email_stats()
        if estats:
            dist = pd.DataFrame(list(estats["word_count_distribution"].items()), columns=["Words", "Count"])
            st.bar_chart(dist.set_index("Words"))
        st.markdown('</div>', unsafe_allow_html=True)

    # 2. PERFORMANCE & HISTORY
    st.markdown("### 📈 SYSTEM PERFORMANCE & AUDIT LOGS")
    metrics_data = load_metrics()
    if metrics_data:
        dfm = pd.DataFrame(metrics_data)
        dfm['timestamp'] = pd.to_datetime(dfm['timestamp'])
        
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Avg Response", f"{dfm['response_time'].mean():.2f}s")
        m_col2.metric("Avg Quality", f"{dfm['approx_accuracy'].mean():.1f}%")
        m_col3.metric("Total Sessions", len(dfm))
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Response Time (Latency) Trends**")
            st.line_chart(dfm.set_index('timestamp')['response_time'])
        with c2:
            st.markdown("**Knowledge Retrieval Quality (FAISS Distance)**")
            st.line_chart(dfm.set_index('timestamp')['similarity_score'])
        
        st.markdown("#### 📜 RECENT QUERY HISTORY")
        st.dataframe(dfm.sort_values('timestamp', ascending=False), use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 FULL SYSTEM REBOOT"):
        st.cache_resource.clear()
        st.rerun()

# Fixed Branding
st.markdown("<div class='footer-pin'>BUILD BY CHARAN KARTHIK</div>", unsafe_allow_html=True)
