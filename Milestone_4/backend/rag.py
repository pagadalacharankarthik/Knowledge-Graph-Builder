import os
import json
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from groq import Groq
from graph import get_graph_context

# Initialize globals
_index = None
_model = None
_df = None

def load_vector_db(csv_path=None):
    if csv_path is None:
        csv_path = os.path.join(os.path.dirname(__file__), 'data', 'cleaned_enron_emails.csv')
    
    global _index, _model, _df
    index_path = os.path.join(os.path.dirname(__file__), 'faiss_index')
    
    print(f"Loading data from {csv_path}...")
    try:
        _df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: {csv_path} not found.")
        return False
        
    if 'clean_message' not in _df.columns and 'message' in _df.columns:
        _df['clean_message'] = _df['message'].astype(str)
    
    # NEW: Safety check - ensure normalized_entities exists globally
    if 'normalized_entities' not in _df.columns:
        if 'entities' in _df.columns:
            _df['normalized_entities'] = _df['entities'].apply(lambda e: e if isinstance(e, list) else (str(e).split(",") if isinstance(e, str) else []))
        else:
            _df['entities'] = [[] for _ in range(len(_df))]
            _df['normalized_entities'] = [[] for _ in range(len(_df))]

    # Pre-process search text
    _df["search_text"] = _df["clean_message"].astype(str)
    
    print("Loading embedding model (all-MiniLM-L6-v2)")
    _model = SentenceTransformer("all-MiniLM-L6-v2")
    
    if os.path.exists(index_path):
        print(f"Loading existing FAISS index from {index_path}")
        _index = faiss.read_index(index_path)
    else:
        print("Creating new FAISS index (encoding 20,000 emails)...")
        documents = _df["search_text"].tolist()
        embeddings = _model.encode(documents, batch_size=64, show_progress_bar=True)
        embeddings = np.array(embeddings).astype('float32')
        
        _index = faiss.IndexFlatL2(embeddings.shape[1])
        _index.add(embeddings)
        faiss.write_index(_index, index_path)
        print(f"Vector Index saved to {index_path}")
        
    print("Vector DB ready.")
    return True

def retrieve_context(question):
    global _df, _index, _model
    if _index is None or _model is None or _df is None:
        if not load_vector_db():
            return [], []
            
    # CRITICAL: Ensure normalized_entities exists just-in-time
    if "normalized_entities" not in _df.columns:
        print("Recovering missing columns just-in-time...")
        if "entities" in _df.columns:
            _df["normalized_entities"] = _df["entities"].apply(lambda e: e if isinstance(e, list) else (str(e).split(",") if isinstance(e, str) else []))
        else:
            _df["normalized_entities"] = [[] for _ in range(len(_df))]

    query_vector = _model.encode([question])
    distances, indices = _index.search(query_vector, 3) 
    
    matched_rows = _df.iloc[indices[0]]
    email_context = matched_rows["clean_message"].tolist() if "clean_message" in matched_rows.columns else []
    
    # Defensive entity extraction
    top_entities = []
    if not matched_rows.empty and "normalized_entities" in matched_rows.columns:
        top_entities = matched_rows["normalized_entities"].iloc[0]
        if not isinstance(top_entities, list): top_entities = []
    
    graph_context = []
    if len(top_entities) > 0:
        try:
            graph_context = get_graph_context(top_entities[0])
        except:
            graph_context = []
            
    return email_context, graph_context

def answer_question(question):
    try:
        email_ctx, graph_ctx = retrieve_context(question)
    except Exception as e:
        print(f"Retrieval Error: {e}")
        return {"answer": f"Error during retrieval: {e}", "retrieved_emails": [], "retrieved_graph": []}
    
    if not email_ctx:
        return {"answer": "Not found in retrieved data.", "retrieved_emails": [], "retrieved_graph": []}
        
    context_str = f"Emails:\n{email_ctx}\n\nGraph Relationships:\n{graph_ctx}"
    
    api_key = os.environ.get("LLM_API_KEY")
    try:
        client = Groq(api_key=api_key)
    except Exception as e:
        return {"answer": f"API Error: {e}", "retrieved_emails": email_ctx, "retrieved_graph": graph_ctx}
    
    system_message = """You are an enterprise email analysis assistant.
Your task is to answer user questions based *only* on the provided email context and graph relationships.
You MUST output your answer in a strict JSON format, and ONLY the JSON object. Do not include any other text, explanations, or formatting outside the JSON object.

JSON Schema:
{
  "answer": "Your comprehensive answer based *only* on the provided context. If the information is not found, state EXACTLY 'Not found in retrieved data'.",
  "extracted_entities": ["List of relevant entities (e.g., names, companies) mentioned in the answer. Empty list if none."]
}

# Rules:
1. Do not use external knowledge.
2. Do not assume anything not explicitly stated in the provided context.
3. Your 'answer' should be concise and directly address the 'question' using the provided 'Email Context' and 'Graph Relationships'.
4. Ensure 'extracted_entities' are genuinely present in the relevant context or answer.
5. If the answer cannot be found in the provided context, the 'answer' field MUST be exactly 'Not found in retrieved data'."""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Question: {question}\nContext:\n{context_str}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        
        result_content = response.choices[0].message.content
        result_json = json.loads(result_content)
        
        # Enforce rule over hallucination
        if "Not found in retrieved data" in result_json.get("answer", ""):
            result_json["answer"] = "Not found in retrieved data."
            
    except Exception as e:
        result_json = {"answer": f"Error generating answer: {e}", "extracted_entities": []}
        
    return {
        "answer": result_json.get("answer", "Not found in retrieved data."),
        "extracted_entities": result_json.get("extracted_entities", []),
        "retrieved_emails": email_ctx,
        "retrieved_graph": graph_ctx
    }
