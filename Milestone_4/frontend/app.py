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

# Custom Premium CSS Injection (Pastel & Black Theme)
st.markdown("""
    <style>
        .main {
            background-color: #ffffff;
            color: #000000;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        [data-testid="stSidebar"] {
            background-color: #fce4ec; /* Pale Pink */
            border-right: 2px solid #000000;
        }
        h1, h2, h3 {
            color: #000000;
            font-weight: 800;
        }
        .query-box {
            background-color: #fff9c4; /* Pale Yellow */
            border: 2px solid #000000;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 5px 5px 0px #000000;
        }
        .context-box {
            background-color: #e8f5e9; /* Pale Green */
            border: 2px solid #000000;
            border-radius: 10px;
            padding: 15px;
            margin-top: 15px;
        }
        .stButton button {
            background-color: #000000;
            color: #ffffff;
            border-radius: 0px;
            border: 2px solid #000000;
            font-weight: bold;
            transition: all 0.2s;
            width: 100%;
        }
        .stButton button:hover {
            background-color: #fff9c4;
            color: #000000;
        }
        .footer-highlight {
            background-color: #fff9c4;
            border: 3px solid #000000;
            padding: 15px;
            text-align: center;
            font-size: 1.2em;
            font-weight: 900;
            margin-top: 50px;
            border-radius: 10px;
            box-shadow: 8px 8px 0px #000000;
        }
        .stMetric {
            background-color: #ffffff;
            border: 1px solid #000000;
            padding: 10px;
            border-radius: 5px;
        }
    </style>
""", unsafe_allow_html=True)

# Main Title
st.markdown("<h1 style='text-align: center;'>🧬 Enron Intelligence Graph</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-style: italic;'>Enterprise-scale knowledge discovery using RAG & Neo4j</p>", unsafe_allow_html=True)

# Initialize Session State
if 'db_loaded' not in st.session_state:
    with st.spinner("Loading 20,000 email intelligence..."):
        st.session_state.db_loaded = load_vector_db()

# Main Layout: 2 Columns
col_query, col_graph = st.columns([1.1, 1], gap="medium")

with st.sidebar:
    st.header("📊 Analytics")
    st.metric("Total Archive", "20,000 Mails")
    st.metric("Graph Nodes", "5,000 Entities")
    st.markdown("---")
    st.subheader("🏆 Leaderboard")
    top_persons = get_top_persons(limit=8)
    if top_persons:
        for p in top_persons:
            st.markdown(f"- **{p['name'].title()}** ({p['connections']})")
    else:
        st.info("No graph data.")

with col_query:
    st.markdown("### 🔍 Knowledge Query")
    with st.container():
        st.markdown('<div class="query-box">', unsafe_allow_html=True)
        query = st.text_input("What would you like to discover?", placeholder="e.g. Who is Alan Aronowitz?")
        if st.button("RUN ANALYSIS 🚀"):
            if query:
                with st.spinner("Analyzing..."):
                    res = answer_question(query)
                    st.markdown("#### 💡 AI Synthesis")
                    st.success(res['answer'])
                    
                    st.markdown("#### 📄 Evidence & Context")
                    tabs = st.tabs(["📧 Emails", "🕸️ Relationships"])
                    with tabs[0]:
                        for e in res['retrieved_emails'][:3]:
                            st.info(e)
                    with tabs[1]:
                        for r in res['retrieved_graph'][:5]:
                            st.code(r)
            else:
                st.warning("Enter a query.")
        st.markdown('</div>', unsafe_allow_html=True)

with col_graph:
    st.markdown("### 🕸️ Visual Network")
    nodes, edges = get_graph_data_for_visualization(limit=40)
    if nodes:
        net = Network(height="500px", width="100%", bgcolor="#ffffff", font_color="#000000")
        for node, lbl in nodes:
            net.add_node(node, label=node, color="#fff9c4", borderWidth=2, size=20)
        for src, tgt in edges:
            net.add_edge(src, tgt, color="#000000")
        
        try:
            path = os.path.join(os.path.dirname(__file__), "temp_graph.html")
            net.save_graph(path)
            with open(path, "r", encoding="utf-8") as f:
                html_data = f.read()
            components.html(html_data, height=520)
        except Exception as e:
            st.error(f"Graph Error: {e}")
    else:
        st.info("The Knowledge Graph is empty. Initialize database to see relationships.")

# Bottom Highlighted Branding
st.markdown("""
    <div class="footer-highlight">
        🚀 BUILD BY CHARAN KARTHIK
    </div>
""", unsafe_allow_html=True)
