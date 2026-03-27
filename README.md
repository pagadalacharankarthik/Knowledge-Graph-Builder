# 🧠 AI Knowledge Graph Builder for Enterprise Intelligence
Built by **Charan Karthik**

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Neo4j](https://img.shields.io/badge/Neo4j-008CC1?style=for-the-badge&logo=neo4j&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-f55036?style=for-the-badge)
![Llama3](https://img.shields.io/badge/Llama_3-0467DF?style=for-the-badge)
![FAISS](https://img.shields.io/badge/FAISS-FFB100?style=for-the-badge)

**Live Production App:** [https://knowledge-graph-builder-001.streamlit.app/](https://knowledge-graph-builder-001.streamlit.app/)

**Agile Project Tracking:** [Agile Project Sheet (Excel)](CharanKarthik_Agile_Sheet.xlsx)

---

## 🚀 Project Vision & Outcomes
This project develops an AI-powered platform that automatically builds dynamic **Knowledge Graphs** from the **Enron Email Dataset**. By combining **RAG pipelines**, **embeddings**, and **semantic search**, the platform enables executives, consultants, and researchers to uncover hidden relationships across large datasets. With an interactive graph dashboard, users can explore entities, connections, and insights to improve strategic decision-making.

### Key Outcomes:
- **Automated Extraction**: Seamless extraction of entities and relationships from multi-source data.
- **Dynamic Construction**: Real-time knowledge graph building and incremental updates.
- **Semantic Intelligence**: RAG-powered semantic search across complex enterprise datasets.
- **Interactive Exploration**: High-fidelity dashboards for graph visualization and drill-down analysis.
- **Faster Decisions**: Actionable intelligence for rapid, informed business strategies.

---

## 🧩 Modules Implemented

### 1. Data Ingestion & Processing Layer
- Connects to enterprise sources (databases, emails, docs).
- Cleans, normalizes, and indexes raw data for the retrieval pipeline.

### 2. Entity & Relationship Extraction Engine
- Uses LLM-based NER (Named Entity Recognition) and relation extraction.
- Creates structured triples (**entity–relation–entity**) for the graph database.

### 3. Graph Construction & Storage Hub
- Builds and stores knowledge graphs in **Neo4j**.
- Supports large-scale graph queries and persistent storage of relationships.

### 4. RAG + Semantic Search Layer
- Uses **FAISS** embeddings and **Groq LLM (Llama-3)**.
- Enables contextual Q&A and intelligent knowledge retrieval.

### 5. Interactive Graph Dashboard
- Provides visual graph exploration using **Streamlit** and **PyVis**.
- Allows filtering, search, and deep-dive analysis of topological nodes.

---

## 🏁 Development Milestones

| Milestone | Objective | Technical Details |
| :--- | :--- | :--- |
| **Milestone 1** | Data Ingestion & Schema Design | Build ingestion pipelines using Pandas, define Neo4j knowledge graph schemas (Person, Org, Loc). |
| **Milestone 2** | Entity Extraction & Graph Building | Apply LLM-based NER to extract triples; use Cypher to populate Neo4j and validate relationship density. |
| **Milestone 3** | Semantic Search & RAG Pipelines | Integrate Sentence-Transformers for embeddings, use FAISS for vector indexing, and build the hybrid RAG logic. |
| **Milestone 4** | Dashboard & Deployment | Build the unified Streamlit interface, integrate dynamic PyVis graph visualizations, and deploy to Streamlit Cloud. |

### Evaluation Criteria:
- **Phase 1**: Data ingestion functional; baseline schema defined.
- **Phase 2**: Knowledge graph successfully built; nodes & relations extracted.
- **Phase 3**: Semantic search and RAG engine operational with low latency.
- **Phase 4**: Dashboard fully deployed and live for enterprise intelligence.

---

## 🧩 Technical Deep Dive

### 1. Hybrid RAG (Retrieval-Augmented Generation)
The system uses a unique hybrid retrieval strategy:
-   **Vector Search**: Finds semantically similar emails based on the query.
-   **Graph Context**: For each retrieved email, the system extracts key entities (PERSON, ORG) and queries Neo4j to find their immediate relationships (e.g., who else they are related to).
-   **Context Fusion**: Both the raw email text and the graph relationship triplets are fed into the LLM as high-density context.

### 2. Vector Database & Embeddings
-   **Model**: `all-MiniLM-L6-v2` (Sentence-Transformers).
-   **Storage**: **FAISS** (Facebook AI Similarity Search).
-   **Process**: Emails are cleaned, concatenated with their entity metadata, and encoded into 384-dimensional vectors for fast L2-distance similarity search.

### 3. Neo4j Knowledge Graph
-   **Nodes**: `PERSON`, `ORG`, `GPE`, `DATE`.
-   **Relationships**: `RELATED_TO`.
-   **Logic**: Uses a robust triplet extraction pipeline that canonicalizes entity names (e.g., merging "Ken Lay" and "Kenneth Lay") to ensure graph density and accuracy.

---

## 📂 Full Project Structure
```text
project/
├── Milestone_4/                # PRODUCTION: Unified Application
│   ├── frontend/
│   │   └── app.py              # Main Streamlit Dashboard
│   └── backend/
│       ├── rag.py              # Hybrid RAG & Vector Search Logic
│       ├── graph.py            # Neo4j Graph Query Interface
│       ├── initialize_db.py    # Database & Index Initialization Script
│       └── metrics.py          # Latency & Accuracy Telemetry
├── Data Ingestion Milestone 1/ # RESEARCH: Preprocessing Scripts
├── Milestone 2/                # RESEARCH: Graph Construction Notebooks
├── Milestone 3/                # RESEARCH: Vector/RAG Prototyping
├── data/                       # External dataset pointers
├── requirements.txt            # Global Dependencies
├── LICENSE                     # MIT License
└── README.md                   # Project Overview & SOP
```

---

## 🛠️ Setup & SOP (Standard Operating Procedure)

### Standard Operating Procedure (SOP)
1.  **Environment Setup**: Ensure Python 3.9+ is active and all API keys (Groq, Neo4j) are ready.
2.  **Dependency Handling**: Install all packages from the root `requirements.txt`.
3.  **Graph Initialization**: Run `initialize_db.py` to wipe/populate the Neo4j instance.
4.  **Application Launch**: Start Streamlit through the `frontend/app.py` entry point.

---

## 🚀 How to Run Locally

### Step 1: Initialize the Database (One-time)
```bash
cd "Milestone_4/backend"
python initialize_db.py
cd ../..
```

### Step 2: Launch the Dashboard
```bash
streamlit run "Milestone_4/frontend/app.py"
```

---

## 🌐 Deployment Configuration
Deployed to **Streamlit Cloud**. Requires the following Secrets:
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- `LLM_API_KEY` (Groq)

---

## 🔍 Example Queries
- *"Who are the key players in Energy Trading?"*
- *"Summarize Kenneth Lay's involvement in company strategy."*
- *"Detail the communication between Jeffrey Skilling and Andrew Fastow."*
- *"What are the most frequent organizations mentioned in the data?"*
- *"Find all mentions of sensitive or confidential deal structures."*

---
© 2026 AI KNOWLEDGE GRAPH system | Built by **Charan Karthik**
