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
    global _index, _model, _df
    
    if csv_path is None:
        csv_path = os.path.join(os.path.dirname(__file__), 'data', 'cleaned_enron_emails.csv')
    
    index_path = os.path.join(os.path.dirname(__file__), 'faiss_index')
    
    print(f"Loading data from {csv_path}...")
    try:
        _df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Critical Error: {e}")
        return False
        
    # ULTIMATE COLUMN RECOVERY: Scan for message content
    text_cols = ['clean_message', 'message', 'body', 'content', 'text', 'Payload']
    found_col = None
    for col in text_cols:
        if col in _df.columns:
            found_col = col
            break
            
    if not found_col:
        # Fallback to the first object/string column that isn't ID-like
        for col in _df.columns:
            if _df[col].dtype == 'object' and "id" not in col.lower():
                found_col = col
                break
    
    if not found_col:
        print("Error: No text column identified.")
        return False
        
    _df['clean_message'] = _df[found_col].astype(str)
    _df["search_text"] = _df['clean_message']
    
    # ENTITY RECOVERY
    if 'normalized_entities' not in _df.columns:
        if 'entities' in _df.columns:
            _df['normalized_entities'] = _df['entities'].apply(lambda e: e if isinstance(e, list) else (str(e).split(",") if isinstance(e, str) else []))
        else:
            _df['normalized_entities'] = [[] for _ in range(len(_df))]

    print("Loading embedding model...")
    _model = SentenceTransformer("all-MiniLM-L6-v2")
    
    if os.path.exists(index_path):
        try:
            _index = faiss.read_index(index_path)
        except:
            _index = None # Force recreation if corrupted
            
    if _index is None:
        print("Building new index...")
        documents = _df["search_text"].tolist()
        embeddings = _model.encode(documents, convert_to_numpy=True).astype('float32')
        _index = faiss.IndexFlatL2(embeddings.shape[1])
        _index.add(embeddings)
        try:
            faiss.write_index(_index, index_path)
        except: pass
        
    print("Vector DB ready.")
    return True

import time

def retrieve_context(question):
    global _df, _index, _model
    start_time = time.time()
    
    # 1. Mandatory Singleton Check
    if _index is None or _model is None or _df is None:
        if not load_vector_db():
            return [], [], 0.0
            
    # 2. Schema Guard
    try:
        if "normalized_entities" not in _df.columns:
            _df["normalized_entities"] = [[] for _ in range(len(_df))]
    except: pass

    # 3. Retrieval
    try:
        query_vector = _model.encode([str(question)])
        distances, indices = _index.search(query_vector, 3) 
        matched_rows = _df.iloc[indices[0]]
    except Exception as e:
        return [], [], 0.0
    
    # 4. Content Extraction
    email_context = matched_rows["clean_message"].tolist() if "clean_message" in matched_rows.columns else []
    
    # 5. Entity & Graph Extraction
    graph = []
    try:
        if "normalized_entities" in matched_rows.columns:
            ents = matched_rows["normalized_entities"].iloc[0]
            if isinstance(ents, list) and len(ents) > 0:
                graph = get_graph_context(ents[0])
    except: pass
            
    latency = time.time() - start_time
    return email_context, graph, latency

def answer_question(question):
    try:
        email_ctx, graph_ctx, latency = retrieve_context(question)
    except:
        return {"question": question, "answer": "System Busy", "extracted_entities": [], "retrieval_latency_seconds": 0.0}
    
    if not email_ctx:
        return {"question": question, "answer": "Not found in emails", "extracted_entities": [], "retrieval_latency_seconds": latency}
        
    api_key = os.environ.get("LLM_API_KEY")
    if not api_key:
        return {"question": question, "answer": "LLM_API_KEY missing", "extracted_entities": [], "retrieval_latency_seconds": latency}
        
    system_message = """You are an enterprise email analysis assistant.
Your task is to answer user questions based *only* on the provided email context and graph relationships.
You MUST output your answer in a strict JSON format, and ONLY the JSON object. Do not include any other text, explanations, or formatting outside the JSON object.

JSON Schema:
{
  "question": "The original question asked by the user.",
  "answer": "Your comprehensive answer based *only* on the provided context. If the information is not found, state EXACTLY 'Not found in emails'.",
  "extracted_entities": ["List of relevant entities (e.g., names, companies) mentioned in the answer. Empty list if none."]
}

# Rules:
1. Do not use external knowledge.
2. Do not assume anything not explicitly stated in the provided context.
3. Your 'answer' should be concise and directly address the 'question' using the provided 'Email Context' and 'Graph Relationships'.
4. Ensure 'extracted_entities' are genuinely present in the relevant context or answer.
5. If the answer cannot be found in the provided context, the 'answer' field MUST be exactly 'Not found in emails'."""

    # MIRROR MILESTONE 3 CONTEXT FORMAT
    context_str = f"Emails:\n{email_ctx}\n\nGraph Relationships:\n{graph_ctx}"
    
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Question: {question}\nContext:\n{context_str}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        res_json = json.loads(response.choices[0].message.content)
        return {
            "question": question,
            "answer": res_json.get("answer", "Not found in emails"),
            "extracted_entities": res_json.get("extracted_entities", []),
            "retrieved_emails": email_ctx, # Kept for UI tabs
            "retrieved_graph": graph_ctx,  # Kept for UI tabs
            "retrieval_latency_seconds": latency
        }
    except Exception as e:
        return {"question": question, "answer": f"Error: {e}", "extracted_entities": [], "retrieval_latency_seconds": latency}
