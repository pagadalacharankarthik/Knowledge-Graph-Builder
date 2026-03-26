# PRODUCTION_VERSION: 4.5.2 (LATEST)
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
import os
import sys

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
        /* Tab height optimization */
        .stTabs [data-baseweb="tab-panel"] {
            max-height: 200px;
            overflow-y: auto;
        }
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

# Grid Layout
left_pane, mid_pane, right_pane = st.columns([0.8, 1.5, 1.5], gap="medium")

# 1. ANALYTICS PANE
with left_pane:
    st.markdown('<div class="control-pane">', unsafe_allow_html=True)
    st.markdown("#### 📊 ARCHIVE STATUS")
    kpis = get_kpis()
    ma, mb, mc = st.columns(3)
    with ma: st.metric("CORPUS", "10K")
    with mb: st.metric("PEOPLE", kpis.get("persons", "0"))
    with mc: st.metric("ORGS", kpis.get("orgs", "0"))
    md, me, mf = st.columns(3)
    with md: st.metric("NODES", kpis.get("nodes", "0"))
    with me: st.metric("EDGES", kpis.get("edges", "0"))
    with mf: st.metric("LOCS", kpis.get("locations", "0"))
    
    st.markdown("<br>#### 🏆 TOP ENTITIES", unsafe_allow_html=True)
    import pandas as pd  # type: ignore
    t1, t2 = st.tabs(["PEOPLE", "ORGS"])
    with t1:
        leaders = get_top_entities("PERSON", limit=10)
        if leaders:
            df_people = pd.DataFrame(leaders)
            st.bar_chart(df_people.set_index('name')['connections'], height=250)
    with t2:
        orgs = get_top_entities("ORG", limit=10)
        if orgs:
            df_orgs = pd.DataFrame(orgs)
            st.bar_chart(df_orgs.set_index('name')['connections'], height=250)
    
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
                        "retrieved_emails_count": len(res.get("retrieved_emails", [])),
                        "retrieval_latency_seconds": res.get("retrieval_latency_seconds", 0.0),
                        "database_total_rows": db_rows
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
    fcol1, fcol2 = st.columns(2)
    with fcol1: node_limit = st.slider("Node Density", min_value=10, max_value=500, value=150, step=50, help="Higher density shows more relationships but may slow the browser.")
    with fcol2: entity_filter = st.selectbox("Entity Filter", ["ALL", "PERSON", "ORG", "LOCATION"])
    nodes, edges = get_graph_data_for_visualization(limit=node_limit, filter_label=entity_filter)
    if nodes:
        top_node = get_most_connected_nodes(limit=1)
        top_name = top_node[0]['name'] if top_node else None
        
        net = Network(height="460px", width="100%", bgcolor="transparent", font_color="#d1d5db")
        net.force_atlas_2based()
        color_map = {"PERSON": "#38bdf8", "ORG": "#818cf8", "LOCATION": "#34d399", "DATE": "#fbbf24"}
        for n, l in nodes:
            node_size = 35 if n == top_name else 15
            net.add_node(n, label=n, color=color_map.get(l, "#f472b6"), size=node_size)
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

# 4. MODEL ANALYTICS SECTION
st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
with st.expander("📊 MODEL ANALYTICS & SYSTEM PERFORMANCE", expanded=False):
    metrics_data = load_metrics()
    if metrics_data:
        import pandas as pd  # type: ignore
        df_metrics = pd.DataFrame(metrics_data)
        df_metrics['timestamp'] = pd.to_datetime(df_metrics['timestamp'])
        
        avg_rt = df_metrics['response_time'].mean()
        avg_acc = df_metrics['approx_accuracy'].mean()
        
        st.markdown("#### Key Performance Indicators")
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Queries", len(df_metrics))
        m2.metric("Avg Response Time", f"{avg_rt:.2f}s")
        m3.metric("Avg Approximated Accuracy", f"{avg_acc:.1f}%")
        
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Response Time Trend (Seconds)**")
            st.line_chart(df_metrics.set_index('timestamp')['response_time'])
            
            st.markdown("**Retrieval Count Distribution**")
            st.bar_chart(df_metrics['retrieved_docs_count'].value_counts())
            
        with c2:
            st.markdown("**Similarity Score Trend (FAISS Distance)**")
            st.line_chart(df_metrics.set_index('timestamp')['similarity_score'])
            
            st.markdown("**Query Volume Over Time**")
            if not df_metrics.empty:
                df_metrics['time_bin'] = df_metrics['timestamp'].dt.strftime('%H:00')
                st.bar_chart(df_metrics.groupby('time_bin').size())
                
        st.markdown("<br>#### 📜 Query History Log", unsafe_allow_html=True)
        display_df = df_metrics[['timestamp', 'query', 'response_time', 'similarity_score', 'approx_accuracy']].copy()
        display_df.sort_values('timestamp', ascending=False, inplace=True)
        st.dataframe(display_df, use_container_width=True)
        
        st.markdown("<br>#### 📧 Email Insights", unsafe_allow_html=True)
        stats = get_email_stats()
        if stats and "word_count_distribution" in stats:
            st.markdown("**Word Count Distribution**")
            df_dist = pd.DataFrame(list(stats["word_count_distribution"].items()), columns=["Length", "Count"])
            st.bar_chart(df_dist.set_index('Length'))
    else:
        st.info("No query metrics recorded yet. Issue a search request to generate telemetry.")

# Fixed Branding
st.markdown("<div class='footer-pin'>BUILD BY CHARAN KARTHIK</div>", unsafe_allow_html=True)
