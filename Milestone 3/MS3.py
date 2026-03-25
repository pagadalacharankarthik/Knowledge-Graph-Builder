# Extracted Code from Milestone 3 Notebook (Copy_of_MS3_01(final).ipynb)

import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from datasets import load_dataset
from groq import Groq
import os

# 1. Load Data
dataset = load_dataset("corbt/enron-emails")
df = dataset["train"].to_pandas().sample(20000, random_state=42)

# 2. Vector DB (FAISS)
model = SentenceTransformer("all-MiniLM-L6-v2")
df["search_text"] = df["text"].astype(str)
embeddings = model.encode(df["search_text"].tolist(), batch_size=64, show_progress_bar=True)
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

# 3. Retrieval Logic
def retrieve_context(question):
    query_vector = model.encode([question])
    distances, indices = index.search(query_vector, 3)
    email_context = df.iloc[indices[0]]["text"].tolist()
    return email_context

# 4. LLM Generation (Groq)
client = Groq(api_key="REPLACE_WITH_YOUR_API_KEY")

def generate_answer(question):
    email_ctx = retrieve_context(question)
    prompt = f"Answer using context:\n{email_ctx}\n\nQuestion: {question}"
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

print("Milestone 3 logic restored.")
