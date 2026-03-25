# 📌 Milestone 3: Semantic Search & RAG Pipeline

## 📖 Overview
Milestone 3 introduces **Retrieval-Augmented Generation (RAG)** to enable intelligent question answering over the dataset.  
It combines semantic search with graph-based retrieval to provide accurate and context-aware responses.

---

## 🎯 Objective
- Build semantic search using embeddings
- Integrate vector search with graph database
- Enable hybrid retrieval (structured + unstructured)
- Generate accurate answers using LLM

---

## ⚙️ Technologies Used
- Python
- FAISS (Vector Search)
- Sentence Transformers
- Neo4j
- LLM (e.g., Llama 3.1 8B Instant)

---

## 🧩 Workflow

### 1. Data Loading
- Load `cleaned_enron_emails.csv`
- Ensure SAME dataset as Milestone 2

---

### 2. Embedding Generation
- Convert `clean_message` into embeddings
- Use model: `all-MiniLM-L6-v2`

---

### 3. Vector Database Creation
- Store embeddings using FAISS
- Enable fast similarity search

---

### 4. Semantic Search
- Convert user query into embedding
- Retrieve top-k similar emails

---

### 5. Graph Retrieval
- Query Neo4j for related entities
- Extract relationships from graph

---

### 6. Hybrid Retrieval
Combine:
- Vector search results (emails)
- Graph relationships (entities)

---

### 7. LLM Answer Generation
- Provide retrieved context to LLM
- Generate answer based ONLY on context

---

## 🔒 Strict Answering Rules
- Do NOT use external knowledge
- Do NOT assume missing data  
- If answer not found, return:


Not found in retrieved data


---

## 📊 Example Flow

User Query
↓
Vector Search (Emails)
↓
Graph Retrieval (Neo4j)
↓
Context Merge
↓
LLM Answer


---

## 📁 Outputs
- Semantic search results
- Graph-based context
- AI-generated answers

---

## ⚠️ Challenges
- Data inconsistency between MS2 and MS3
- Hallucinated LLM responses
- Empty graph results

---

## ✅ Solutions
- Use SAME dataset for both MS2 and MS3
- Apply strict prompt rules
- Combine graph + vector context

---

## 🚀 Outcome
- Built a hybrid RAG system
- Enabled intelligent question answering
- Reduced hallucination using controlled context
- Integrated structured and unstructured data