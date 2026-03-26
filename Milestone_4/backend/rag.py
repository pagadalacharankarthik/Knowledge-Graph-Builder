import os
import time
import json
import pandas as pd  # type: ignore
import numpy as np  # type: ignore
import faiss  # type: ignore
from sentence_transformers import SentenceTransformer  # type: ignore
from groq import Groq  # type: ignore
from graph import get_graph_context  # type: ignore

class KnowledgeCore:
    _instance = None
    
    def __init__(self):
        self.df = None
        self.index = None
        self.model = None
        self.index_path = os.path.join(os.path.dirname(__file__), 'faiss_index')
        
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = KnowledgeCore()  # type: ignore
        return cls._instance

    def load(self, csv_path=None):
        if self.df is not None and self.index is not None:
            return True
            
        if csv_path is None:
            csv_path = os.path.join(os.path.dirname(__file__), 'data', 'cleaned_enron_emails.csv')
        
        print(f"Initializing KnowledgeCore from {csv_path}...")
        try:
            df = pd.read_csv(csv_path)
            # Column Recovery
            text_cols = ['clean_message', 'message', 'body', 'content', 'text', 'Payload']
            found_col = next((c for c in text_cols if c in df.columns), None)
            if not found_col:
                found_col = next((c for c in df.columns if df[c].dtype == 'object' and "id" not in c.lower()), None)
            
            if not found_col: return False
            df['clean_message'] = df[found_col].astype(str)
            
            # Entities Recovery
            if 'normalized_entities' not in df.columns:
                df['normalized_entities'] = df.get('entities', [[] for _ in range(len(df))])
            
            self.df = df
            
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
            
            # Index Load/Build
            if os.path.exists(self.index_path) and not os.path.isdir(self.index_path):
                try:
                    self.index = faiss.read_index(self.index_path)
                except:
                    self.index = None
            
            if self.index is None:
                print("Building Vector Index in batches...")
                docs = self.df['clean_message'].tolist()
                batch_size = 500
                embs = []
                for i in range(0, len(docs), batch_size):
                    embs.append(self.model.encode(docs[i:i+batch_size], convert_to_numpy=True))  # type: ignore
                embeddings = np.vstack(embs).astype('float32')
                self.index = faiss.IndexFlatL2(embeddings.shape[1])
                self.index.add(embeddings)
                try: faiss.write_index(self.index, self.index_path)  # type: ignore
                except: pass
            
            print(f"KnowledgeCore Ready: {len(self.df)} mails.")  # type: ignore
            return True
        except Exception as e:
            print(f"Load Error: {e}")
            return False

def answer_question(question):
    core = KnowledgeCore.get_instance()
    if not core.load():
        return {"question": question, "answer": "Core Engine Failed to Start", "extracted_entities": [], "retrieval_latency_seconds": 0}
        
    start_time = time.time()
    try:
        query_vector = core.model.encode([str(question)])
        distances, indices = core.index.search(query_vector, 5)
        matched_rows = core.df.iloc[indices[0]]
        email_ctx = matched_rows['clean_message'].tolist()
        
        # Graph
        graph_ctx = []
        try:
            ents = matched_rows['normalized_entities'].iloc[0]
            if isinstance(ents, list) and len(ents) > 0:
                graph_ctx = get_graph_context(ents[0])
        except: pass
        
        latency = time.time() - start_time
        db_rows = len(core.df)
    except Exception as e:
        return {"question": question, "answer": f"System Error: {str(e)}", "extracted_entities": [], "retrieval_latency_seconds": 0, "db_rows": 0}

    # Context injection + LLM call
    api_key = os.environ.get("LLM_API_KEY")
    if not api_key:
        return {"question": question, "answer": "LLM_API_KEY missing", "extracted_entities": [], "retrieval_latency_seconds": latency, "db_rows": db_rows}
    
    client = Groq(api_key=api_key)
    context_str = "\n---\n".join(email_ctx)
    graph_str = "\n".join(graph_ctx)
    
    # Milestone 3 System Prompt (Standardized)
    system_prompt = """You are an Enron email analysis assistant.
Answer the question based ONLY on the context below. 
If the information is not present, say 'Not found in emails' but be helpful with related context.
Output in strict JSON:
{
  "question": "...",
  "answer": "...",
  "extracted_entities": ["...", "..."]
}"""

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"EMAIL CONTEXT:\n{context_str}\n\nGRAPH CONTEXT:\n{graph_str}\n\nQUESTION: {question}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        res_json = json.loads(response.choices[0].message.content)
        answer_text = res_json.get("answer", "No answer found")
        
        try:
            from metrics import log_metrics  # type: ignore
            avg_dist = float(distances[0].mean()) if 'distances' in locals() else 0.0
            log_metrics({
                "query": question,
                "response_time": time.time() - start_time,
                "similarity_score": avg_dist,
                "retrieved_docs_count": len(email_ctx),
                "answer_length": len(answer_text)
            })
        except Exception as e:
            print(f"Metrics log error: {e}")

        return {
            "question": question,
            "answer": answer_text,
            "extracted_entities": res_json.get("extracted_entities", []),
            "retrieval_latency_seconds": latency,
            "db_rows": db_rows,
            "retrieved_emails": email_ctx,
            "retrieved_graph": graph_ctx
        }
    except Exception as e:
        return {"question": question, "answer": f"LLM Error: {str(e)}", "extracted_entities": [], "retrieval_latency_seconds": latency, "db_rows": db_rows, "retrieved_emails": email_ctx}
