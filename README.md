# 🧠 AI KNOWLEDGE GRAPH system
Built by **Charan Karthik**

**Live Production App:** [https://knowledge-graph-builder-001.streamlit.app/](https://knowledge-graph-builder-001.streamlit.app/)

**Agile Project Tracking:** [Agile Project Sheet (Excel)](Agile_Sheet.xlsx)

---

## 🚀 Project Vision & Outcomes
This project develops an AI-powered platform that automatically builds dynamic **Knowledge Graphs** from enterprise data sources such as documents, emails, and databases. By combining **RAG pipelines**, **embeddings**, and **semantic search**, the platform enables executives, consultants, and researchers to uncover hidden relationships across large datasets. With an interactive graph dashboard, users can explore entities, connections, and insights to improve strategic decision-making.

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

| Milestone | Objective | Key Tasks |
| :--- | :--- | :--- |
| **Milestone 1** | Data Ingestion & Schema Design | Build ingestion pipelines, define knowledge graph schema. |
| **Milestone 2** | Entity Extraction & Graph Building | Apply LLM NER, store results in Neo4j, validate graph. |
| **Milestone 3** | Semantic Search & RAG Pipelines | Integrate embeddings with FAISS, build semantic search. |
| **Milestone 4** | Dashboard & Deployment | Build graph visualization UI, integrate APIs, deploy system. |

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

## 📂 Project Structure
```
project/
├── Milestone_4/            # Final Integrated Application
│   ├── frontend/
│   │   └── app.py          # Dashboard (Streamlit UI)
│   └── backend/
│       ├── rag.py          # RAG (FAISS + LLM) Logic
│       ├── graph.py        # Knowledge Graph (Neo4j) logic
│       ├── initialize_db.py # One-time Database Initialization
│       └── data/
│           └── cleaned_enron_emails.csv # Real Enron Dataset
├── requirements.txt        # Combined Dependencies
└── README.md               # You are here
```

---

## 🛠️ Setup & SOP (Standard Operating Procedure)

### Standard Operating Procedure (SOP)
1.  **Environment Setup**: Ensure Python 3.9+ is active and all API keys (Groq, Neo4j) are ready.
2.  **Dependency Handling**: Install all packages from the root `requirements.txt`.
3.  **Data Generation**: Run the Milestone 1 scripts to produce the `cleaned_enron_emails.csv`.
4.  **Graph Initialization**: Run `initialize_db.py` to wipe/populate the Neo4j instance.
5.  **Application Launch**: Start Streamlit through the `frontend/app.py` entry point.

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

---

## 🌐 How to Deploy to Streamlit Cloud (Live Link Guide)

1.  **GitHub**: Push your entire `Milestone_4` folder to a public GitHub repo.
2.  **Streamlit Share**: Log in and click "New app".
3.  **Main File Path**: Set this to `Milestone_4/frontend/app.py`.
4.  **Secrets (Advanced Settings)**:
    ```toml
    NEO4J_URI = "..."
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "..."
    LLM_API_KEY = "..."
    ```

### 📋 Files to Update for Accuracy
If the app is blank or answers are wrong, ensure you have updated these files in your GitHub repo:
1.  **`Milestone_4/backend/data/cleaned_enron_emails.csv`**: (The 20k rows version).
2.  **`Milestone_4/backend/faiss_index`**: (Generated by running `initialize_db.py` locally).
3.  **`Milestone_4/frontend/app.py`**: (The new restructured UI).
4.  **`requirements.txt`**: (Must have `torch`, `faiss-cpu`, `sentence-transformers`).

---

## 🔍 Example Queries
- *"What were the most discussed topics in the months before the collapse?"*
- *"Who is discussing energy trading?"*
- *"What are the most frequent companies mentioned?"*
- *"What are the patterns in, or most common words in, email subject lines?"*
- *"Who is discussed in relation to the 'energy modeling forum'?"*
- *"Are there any mentions of specific Enron Corp conferences or meeting planning?"*
- *"What are the common topics discussed by Steffes James and Phillip K. Allen?"*
- *"Are there any legal or regulatory concerns regarding ISO tariff confidentiality?"*
- *"What action items were recorded for the Fundamentals Desk?"*
- *"Who is 'Janelle Daniel' communicating with regarding deals?"*
- *"Are there any mentions of the 'Foreign Corrupt Practices Act' (FCPA)?"*
- *"What projects involve 'Tracy Ramsey'?"*
- *"Is there any mention of a 'Deals summary sheet'?"*
- *"Who are the primary contacts for 'climate change strategy'?"*
<!-- Who is discussed in relation to the 'energy modeling forum'?
Are there any mentions of specific Enron Corp conferences or meeting planning?
What are the common topics discussed by Steffes James and Phillip K. Allen?
Are there any legal or regulatory concerns regarding ISO tariff confidentiality?
What action items were recorded for the Fundamentals Desk?
Who is 'Janelle Daniel' communicating with regarding deals?
Are there any mentions of the 'Foreign Corrupt Practices Act' (FCPA)?
What projects involve 'Tracy Ramsey'?
Is there any mention of a 'Deals summary sheet'?
Who are the primary contacts for 'climate change strategy'? -->

---
© 2026 AI Knowledge Graph Builder | Build by **Charan Karthik**
