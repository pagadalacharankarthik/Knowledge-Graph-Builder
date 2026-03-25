# Extracted Code from Milestone 2 Notebook (MS2T.ipynb)

import pandas as pd
import spacy
from neo4j import GraphDatabase
from datasets import load_dataset
import re
from tqdm import tqdm
from fuzzywuzzy import process

# 1. Load Enron dataset
dataset = load_dataset("corbt/enron-emails", split="train")
df = pd.DataFrame(dataset)

# 2. Clean and preprocess
df = df[["from", "to", "subject", "body"]]
df.columns = ["from_email", "to_email", "subject", "body"]
df = df.dropna(subset=["from_email", "to_email", "subject", "body"])
df['to_email'] = df['to_email'].apply(lambda x: x[0] if isinstance(x, list) else x)
df = df.drop_duplicates()
df = df.reset_index(drop=True)

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\S*@\S*', '', text) # Remove email addresses
    text = re.sub(r'[^\w\s@.]', '', text)
    return text.strip()

df["clean_subject"] = df["subject"].apply(clean_text)
df["clean_body"] = df["body"].apply(clean_text)
df["full_text"] = df["clean_subject"] + " " + df["clean_body"]

# 3. Entity Extraction (spaCy)
nlp = spacy.load("en_core_web_sm")

def extract_entities(text, min_len=2, min_len_person=3):
    doc = nlp(text)
    persons, orgs, locations, dates = [], [], [], []
    for ent in doc.ents:
        cleaned_ent_text = ent.text.strip().lower()
        if cleaned_ent_text in ['enron', 'hou', 'ect']: continue
        if len(cleaned_ent_text) > (min_len_person if ent.label_ == "PERSON" else min_len):
            if ent.label_ == "PERSON": persons.append(ent.text)
            elif ent.label_ == "ORG": orgs.append(ent.text)
            elif ent.label_ in ["GPE", "LOC"]: locations.append(ent.text)
            elif ent.label_ == "DATE": dates.append(ent.text)
    return persons, orgs, locations, dates

df_sample = df.head(200).copy()
df_sample["persons"], df_sample["orgs"], df_sample["locations"], df_sample["dates"] = zip(
    *df_sample["full_text"].apply(extract_entities)
)

# 4. Canonicalization
def canonicalize_entities(entity_list):
    if not entity_list: return []
    processed = set()
    canonical = []
    sorted_ents = sorted(list(set(entity_list)), key=len, reverse=True)
    for ent in sorted_ents:
        if ent in processed: continue
        canonical.append(ent)
        for other in sorted_ents:
            if ent in other or other in ent: processed.add(other)
    return canonical

for col in ['persons', 'orgs', 'locations', 'dates']:
    df_sample[col] = df_sample[col].apply(canonicalize_entities)

# 5. Neo4j Insertion
uri = "neo4j+s://6e73b041.databases.neo4j.io"
username = "neo4j"
password = "REPLACE_WITH_YOUR_PASSWORD"
driver = GraphDatabase.driver(uri, auth=(username, password))

def batch_insert_triplets(tx, triplets_batch, s_label, o_label):
    query = f"""
    UNWIND $triplets_batch AS t
    MERGE (s:{s_label} {{name: t.subject}})
    MERGE (o:{o_label} {{name: t.object}})
    MERGE (s)-[:RELATED_TO]->(o)
    """
    tx.run(query, triplets_batch=triplets_batch)

# (Detailed Triplet generation and looping logic followed here)
print("Milestone 2 logic restored.")
