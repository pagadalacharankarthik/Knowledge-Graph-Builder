# Product Requirements Document (PRD): AI KNOWLEDGE GRAPH system

## 1. Project Overview & Evolution
The **Enterprise Intelligence Hub** is a next-generation RAG (Retrieval-Augmented Generation) platform designed to parse, index, and analyze complex unstructured email data (Enron Corpus). It evolved through four critical development milestones:

- **Milestone 1**: Data Pre-processing & Entity Extraction (Cleaning & NER).
- **Milestone 2**: Graph Database Construction (Neo4j Schema & Insertion).
- **Milestone 3**: RAG Pipeline Integration (FAISS Vector Search + Groq LLM).
- **Milestone 4**: Advanced Analytics & Professional Dashboard UI.

## 2. Technical Architecture
The system employs a **Hybrid Intelligence Architecture** that merges semantic vector search with structural graph context.

### A. Data Layer
- **Source**: `cleaned_enron_emails.csv` (Email text, Word count, Entities).
- **Vector Index**: FAISS (L2 Distance) storing 768-D embeddings from HuggingFace Sentence Transformers.
- **Graph Database**: Neo4j storing:
  - **Nodes**: `PERSON`, `ORG`, `LOCATION`, `EMAIL`.
  - **Relationships**: `MENTIONS`, `SENT_TO`, `CONTAINS`.

### B. Logic Layer (Hybrid RAG)
1.  **Query Input**: User submits a natural language query.
2.  **Vector Retrieval**: FAISS finds top-K semantically similar emails based on the query embedding.
3.  **Graph Retrieval**: NER extracts entities from the query; Neo4j finds first-degree relationships (subgraph) for those entities.
4.  **Context Synthesis**: Both the raw email snippets and the graph relationship strings are injected into the Prompt Template.
5.  **Inference**: Groq (Llama-3-70b) generates a fact-based answer grounded in the retrieved context.

## 3. Core Feature Set

### 🔎 Intelligence Hub (Operational Tab)
- **Topological Status**: Live KPI metrics (Corpus Size, People, Organizations, Graph Vitality).
- **Neural Trace (Audit)**: Transparent view of the "Mental Model" behind each AI response, showing exact FAISS references and Neo4j paths.
- **Topology Overview**: Interactive visualization using `ForceAtlas2` layout to show hubs and connections.

### 📈 Advanced Analytics (Strategic Tab)
- **Entity Centrality**: Automated "Hub" detection identifying the most influential people/orgs in the network.
- **Email Distributions**: Insights into the data corpus (Word Count spread, most active entities).
- **Audit Logging**: Performance telemetry tracking Latency (seconds) and Knowledge Quality (Similarity scores).

## 4. Setup & Environment
- **Runtime**: Streamlit (Python-based).
- **Secrets**: `LLM_API_KEY` (Groq), `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`.
- **Dependencies**: `streamlit`, `pyvis`, `neo4j`, `faiss-cpu`, `sentence-transformers`, `pandas`.

## 5. Algorithmic Detail
- **Centrality**: Computed via degree centrality (number of connections) per label in Neo4j.
- **Accuracy Tracking**: Uses the FAISS distance score as an inverse proxy for retrieval confidence.
- **Visualization**: Nodes are color-coded (Blue=Person, Purple=Org, Green=Location) and sized by connection importance.

---
*This document serves as the master blueprint for the Enterprise Intelligence Hub system. Managed and updated for future scalability.*
