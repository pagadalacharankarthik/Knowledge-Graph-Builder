# Product Requirements Document (PRD): Enterprise Intelligence Hub

## 🎯 Project Vision
To transform the static Enron email dataset into a dynamic, real-time Intelligence Hub that combines **Vector Retrieval (FAISS)** and **Graph Knowledge (Neo4j)** to provide deep contextual insights and network analytics.

## 🏗️ System Architecture
The platform is built on a **Modular RAG (Retrieval-Augmented Generation) Architecture**:
1.  **Ingestion Layer**: Pre-processed CSV email data with extracted entities (People, Orgs, Locations).
2.  **Storage Layer (Hybrid)**:
    - **Vector DB**: FAISS index storing 768-dim embeddings for semantic search.
    - **Graph DB**: Neo4j instance storing entities and relational connections.
3.  **Inference Layer**: Groq-powered LLM (Llama-3) for context-aware responses.
4.  **UI Layer**: Professional-grade Streamlit dashboard with custom dark-mode CSS and `PyVis` topological visualization.

## 🚀 Key Features

### 🔎 Intelligence Hub (Operational Layer)
- **Contextual Q&A**: Hybrid search querying both Vector and Graph databases.
- **Neural Trace**: Detailed audit trail showing retrieved email content and graph relationships.
- **Topology Overview**: Interactive network visualization with node density and entity-type filters (PERSON, ORG, LOC).

### 📈 Advanced Analytics (Insight Layer)
- **KPI Metrics**: Real-time counts for database entities and relationships.
- **Network Centrality**: Automated identification of "Hub" entities using graph degree Centrality.
- **Data Distributions**: Visual analysis of email word counts and entity mention frequency.
- **System Telemetry**: Automated logging of latency, accuracy, and similarity scores.

## 🛠️ Technical Specifications
- **Frontend**: Streamlit 1.30+
- **Graph Engine**: Neo4j Desktop / Aura
- **Vector Engine**: FAISS (Facebook AI Similarity Search)
- **LLM**: Groq (Llama-3-70b/8b)
- **Visualization**: PyVis (NetworkX backend)
- **Data Handling**: Pandas (Metadata buffering)

## 🛡️ Data Privacy & Security
- **Telemetry**: Local `metrics.csv` for session audit logs.
- **API Security**: Environment-variable based key management (`LLM_API_KEY`).
- **Data Integrity**: Optimized caching to prevent redundant Neo4j/FAISS reloads.

---
*Created for future development and platform expansion.*
