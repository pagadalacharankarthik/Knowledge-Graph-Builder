from graph import build_knowledge_graph
from rag import load_vector_db
import os

# Ensure the data directory exists and the file is in the right place
csv_path = os.path.join(os.path.dirname(__file__), 'data', 'cleaned_enron_emails.csv')

if os.path.exists(csv_path):
    print(f"Found dataset at {csv_path}. Starting Full Initialization...")
    try:
        # 1. Build Knowledge Graph (Neo4j)
        build_knowledge_graph(csv_path)
        print("1. Knowledge Graph (Neo4j) initialization complete.")
        
        # 2. Build FAISS Index (Vector DB)
        print("2. Starting FAISS Vector Indexing (This will save 'faiss_index' file)...")
        load_vector_db(csv_path)
        print("FAISS Indexing complete.")
        
        print("\n=== SYSTEM FULLY INITIALIZED AND READY ===")
    except Exception as e:
        print(f"Error during initialization: {e}")
else:
    print(f"Error: {csv_path} not found.")
