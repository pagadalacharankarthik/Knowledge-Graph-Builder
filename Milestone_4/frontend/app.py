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
st.markdown("Query the Enron dataset through an advanced Retrieval-Augmented Generation (RAG) and Neo4j Knowledge Graph system.")

# Custom Premium UI (Dark Slate & Electric Blue)
st.markdown("""
    <style>
        .main {
            background-color: #0f172a;
            color: #f1f5f9;
            font-family: 'Inter', sans-serif;
        }
        [data-testid="stSidebar"] {
            background-color: #1e293b;
            border-right: 1px solid #334155;
        }
        .stMetric {
            background-color: #1e293b !important;
            border: 1px solid #334155 !important;
            padding: 15px !important;
            border-radius: 12px !important;
        }
        .stMetric [data-testid="stMetricValue"] {
            color: #38bdf8 !important;
        }
        .query-card {
            background: rgba(30, 41, 59, 0.7);
            border: 1px solid #334155;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
        }
        .answer-highlight {
            background: linear-gradient(90deg, #1e293b, #0f172a);
            border-left: 4px solid #38bdf8;
            padding: 20px;
            border-radius: 8px;
            margin: 15px 0;
            color: #e2e8f0;
            line-height: 1.6;
        }
        .stButton button {
            background: linear-gradient(135deg, #38bdf8, #1d4ed8);
            color: white;
            border: none;
            padding: 10px 24px;
            border-radius: 8px;
            font-weight: 600;
            width: 100%;
            transition: all 0.3s ease;
        }
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(56, 189, 248, 0.4);
        }
        .footer-branding {
            text-align: center;
            padding: 40px 0;
            color: #64748b;
            font-size: 0.9em;
            letter-spacing: 1px;
        }
        .highlight-name {
            color: #38bdf8;
            font-weight: 700;
            text-transform: uppercase;
        }
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #0f172a;
        }
        ::-webkit-scrollbar-thumb {
            background: #334155;
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Main Dashboard Interface
st.title("🛡️ Enterprise Intelligence Hub")
st.caption("AI-Powered Knowledge Graph & Contextual Search")

# Initialize Session State
if 'db_loaded' not in st.session_state:
    with st.status("Initializing Knowledge Base...", expanded=True) as status:
        st.write("Loading 10,000 email records...")
        st.session_state.db_loaded = load_vector_db()
        status.update(label="System Ready", state="complete", expanded=False)

# Sidebar: Global Analytics
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=80)
    st.title("Analytics")
    
    st.metric("Total Archive", "10,000 Mails")
    st.metric("Graph Nodes", "5,000+ Entities")
    
    st.markdown("---")
    st.subheader("🏆 Network Leaders")
    top_persons = get_top_persons(limit=8)
    if top_persons:
        for p in top_persons:
            with st.container():
                st.markdown(f"""
                <div style='display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 0.9em;'>
                    <span>{p['name'].title()}</span>
                    <span style='color: #38bdf8;'>{p['connections']}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Neo4j database not connected.")

# Main Content Layout
col_left, col_right = st.columns([1.2, 1], gap="large")

with col_left:
    st.markdown("### 🔍 Knowledge Extraction")
    st.markdown('<div class="query-card">', unsafe_allow_html=True)
    query = st.text_input("Consult the archive:", placeholder="Ask about entities, deals, or discussions...")
    
    if st.button("EXECUTE ANALYSIS"):
        if query:
            with st.spinner("Synthesizing answer..."):
                res = answer_question(query)
                st.markdown("#### 💡 AI Response")
                st.markdown(f'<div class="answer-highlight">{res["answer"]}</div>', unsafe_allow_html=True)
                
                st.markdown("#### 📄 Context Retrieval")
                tabs = st.tabs(["📧 Primary Sources", "🕸️ Graph Relations"])
                with tabs[0]:
                    if res['retrieved_emails']:
                        for i, email in enumerate(res['retrieved_emails'][:3]):
                            with st.expander(f"Source Document #{i+1}"):
                                st.write(email)
                    else:
                        st.warning("No relevant emails found.")
                with tabs[1]:
                    if res['retrieved_graph']:
                        for rel in res['retrieved_graph'][:10]:
                            st.code(rel, language="text")
                    else:
                        st.info("No direct graph relationships identified.")
        else:
            st.error("Please provide a query.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown("### 🕸️ Relationship Topology")
    nodes, edges = get_graph_data_for_visualization(limit=50)
    if nodes:
        net = Network(height="550px", width="100%", bgcolor="#0f172a", font_color="#f1f5f9")
        net.force_atlas_2based()
        
        for node, lbl in nodes:
            color = "#38bdf8" if lbl == "PERSON" else "#818cf8"
            net.add_node(node, label=node, color=color, shadow=True)
        for src, tgt in edges:
            net.add_edge(src, tgt, color="#334155")
        
        try:
            path = os.path.join(os.path.dirname(__file__), "temp_graph.html")
            net.save_graph(path)
            with open(path, "r", encoding="utf-8") as f:
                html_data = f.read()
            components.html(html_data, height=560)
        except Exception as e:
            st.error(f"Visualization Error: {e}")
    else:
        st.warning("Visualization engine waiting for data...")

# Footer
st.markdown(f"""
    <div class="footer-branding">
        DESIGNED & BUILT BY <span class="highlight-name">Charan Karthik</span><br>
        <span style="font-size: 0.8em; opacity: 0.6;">© 2026 Enterprise Intelligence Systems</span>
    </div>
""", unsafe_allow_html=True)
