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

def retrieve_context(question):
    global _df, _index, _model
    
    # 1. Mandatory Singleton Check
    if _index is None or _model is None or _df is None:
        if not load_vector_db():
            return [], []
            
    # 2. Schema Guard (Run every time to be 100% sure)
    try:
        if "normalized_entities" not in _df.columns:
            _df["normalized_entities"] = [[] for _ in range(len(_df))]
        if "clean_message" not in _df.columns:
            # Last resort: find first object column
            for c in _df.columns:
                if _df[c].dtype == 'object':
                    _df["clean_message"] = _df[c].astype(str)
                    break
    except: pass

    # 3. Retrieval
    try:
        query_vector = _model.encode([str(question)])
        distances, indices = _index.search(query_vector, 3) 
        matched_rows = _df.iloc[indices[0]]
    except Exception as e:
        print(f"Retrieval Logic Error: {e}")
        return [], []
    
    # 4. Content Extraction
    email_context = []
    if "clean_message" in matched_rows.columns:
        email_context = matched_rows["clean_message"].tolist()
    
    # 5. Entity & Graph Extraction
    graph_context = []
    try:
        # Use column indexing instead of name access for maximum safety
        if "normalized_entities" in matched_rows.columns:
            col_pos = matched_rows.columns.get_loc("normalized_entities")
            top_entities = matched_rows.iloc[0, col_pos]
            if isinstance(top_entities, list) and len(top_entities) > 0:
                graph_context = get_graph_context(top_entities[0])
            elif isinstance(top_entities, str):
                # Handle stringified lists from CSV
                try:
                    ents = eval(top_entities)
                    if isinstance(ents, list) and len(ents) > 0:
                        graph_context = get_graph_context(ents[0])
                except: pass
    except:
        pass
            
    return email_context, graph_context

def answer_question(question):
    try:
        email_ctx, graph_ctx = retrieve_context(question)
    except Exception as e:
        return {"answer": f"System Busy. Error: {e}", "retrieved_emails": [], "retrieved_graph": []}
    
    if not email_ctx:
        return {"answer": "No records found for this query.", "retrieved_emails": [], "retrieved_graph": []}
        
    context_str = f"Context:\n{email_ctx}\n\nGraph:\n{graph_ctx}"
    
    api_key = os.environ.get("LLM_API_KEY")
    if not api_key:
        return {"answer": "LLM_API_KEY missing in Environment.", "retrieved_emails": email_ctx, "retrieved_graph": graph_ctx}
        
    try:
        client = Groq(api_key=api_key)
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a professional Intelligence Analyst. Answer based ONLY on provided context. Be concise."},
                {"role": "user", "content": f"Query: {question}\n\n{context_str}"}
            ],
            model="llama-3.3-70b-versatile",
        )
        return {
            "answer": chat_completion.choices[0].message.content,
            "retrieved_emails": email_ctx,
            "retrieved_graph": graph_ctx
        }
    except Exception as e:
        return {"answer": f"LLM Error: {e}", "retrieved_emails": email_ctx, "retrieved_graph": graph_ctx}
