import os
import pandas as pd
import spacy
import re
from neo4j import GraphDatabase
from fuzzywuzzy import process
from tqdm import tqdm

import subprocess
import sys

# Connect to Neo4j
def get_driver():
    uri = os.environ.get("NEO4J_URI", "neo4j+s://196a05d2.databases.neo4j.io")
    username = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "RukNdqHXMzDPd-BhkFXvHp4TbkhXH04b6sr1YQEZGIw")
    try:
        return GraphDatabase.driver(uri, auth=(username, password))
    except Exception as e:
        print(f"Error connecting to Neo4j: {e}")
        return None

def extract_entities(text, min_len=2, min_len_person=3):
    try:
        # Self-healing spacy loader
        try:
            nlp = spacy.load("en_core_web_sm")
        except:
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            nlp = spacy.load("en_core_web_sm")
            
        doc = nlp(str(text))
        persons, orgs, locations, dates = [], [], [], []

        for ent in doc.ents:
            current_min_len = min_len_person if ent.label_ == "PERSON" else min_len
            cleaned_ent_text = ent.text.strip().lower()

            if cleaned_ent_text in ['enron', 'hou', 'ect']:
                continue

            if len(cleaned_ent_text) > current_min_len:
                if ent.label_ == "PERSON":
                    persons.append(ent.text)
                elif ent.label_ == "ORG":
                    orgs.append(ent.text)
                elif ent.label_ in ["GPE", "LOC"]:
                    locations.append(ent.text)
                elif ent.label_ == "DATE":
                    dates.append(ent.text)
        return persons, orgs, locations, dates
    except Exception:
        # Fallback to simple extraction
        words = str(text).split()
        ents = [w for w in words if w[0].isupper() and len(w) > 2]
        return list(set(ents)), [], [], []

def canonicalize_entities(entity_list, threshold=80):
    if not entity_list:
        return []
    canonical_forms = []
    processed_entities = set()
    sorted_entities = sorted(list(set(entity_list)), key=len, reverse=True)

    for current_entity in sorted_entities:
        if current_entity in processed_entities:
            continue
        best_match = current_entity
        for other_entity in sorted_entities:
            if current_entity == other_entity or other_entity in processed_entities:
                continue
            if current_entity in other_entity or other_entity in current_entity:
                processed_entities.add(other_entity)
        canonical_forms.append(best_match)
        processed_entities.add(best_match)

    return sorted(list(set(canonical_forms)))

def build_knowledge_graph(csv_path):
    print(f"Building Neo4j Graph from {csv_path}...")
    df = pd.read_csv(csv_path)
    if 'full_text' not in df.columns and 'clean_message' in df.columns:
        df['full_text'] = df['clean_message']
        
    df = df.head(5000) # Process more for better visualization
    
    tqdm.pandas()
    df["persons"], df["orgs"], df["locations"], df["dates"] = zip(*df["full_text"].progress_apply(extract_entities))
    
    df['persons'] = df['persons'].apply(canonicalize_entities)
    df['orgs'] = df['orgs'].apply(canonicalize_entities)
    df['locations'] = df['locations'].apply(canonicalize_entities)
    df['dates'] = df['dates'].apply(canonicalize_entities)
    
    def combine_entities(row):
        return [(p, 'PERSON') for p in row['persons']] + \
               [(o, 'ORG') for o in row['orgs']] + \
               [(l, 'LOCATION') for l in row['locations']] + \
               [(d, 'DATE') for d in row['dates']]

    df['all_entities'] = df.apply(combine_entities, axis=1)
    
    triplets = []
    for _, row in df.iterrows():
        ents = row["all_entities"]
        for i in range(len(ents)):
            for j in range(i + 1, len(ents)):
                triplets.append({
                    "subject": ents[i][0], "subject_type": ents[i][1],
                    "relation": "RELATED_TO",
                    "object": ents[j][0], "object_type": ents[j][1]
                })

    if not triplets:
        print("No triplets generated.")
        return

    triplet_df = pd.DataFrame(triplets)
    driver = get_driver()
    if not driver: return
    
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n") # Clear graph
        unique_labels = set(triplet_df['subject_type']).union(set(triplet_df['object_type']))
        for label in unique_labels:
            clean_label = ''.join(e for e in label if e.isalnum())
            session.run(f"CREATE INDEX IF NOT EXISTS FOR (n:{clean_label}) ON (n.name);")
            
        def batch_insert(tx, batch, s_label, o_label):
            q = f"""
            UNWIND $batch AS t
            MERGE (s:{s_label} {{name: t.subject}})
            MERGE (o:{o_label} {{name: t.object}})
            MERGE (s)-[:RELATED_TO]->(o)
            """
            tx.run(q, batch=batch)
            
        for (sub_type, obj_type), group_df in triplet_df.groupby(['subject_type', 'object_type']):
            batch_data = group_df.to_dict(orient='records')
            for i in range(0, len(batch_data), 1000):
                session.execute_write(batch_insert, batch_data[i:i+1000], sub_type, obj_type)
    
    driver.close()
    print("Graph built successfully.")

def get_graph_context(entity):
    driver = get_driver()
    if not driver: return []
    query = """
    MATCH (e {name:$name})-[r]-(n)
    RETURN e.name, type(r), n.name
    LIMIT 5
    """
    relations = []
    try:
        with driver.session() as session:
            result = session.run(query, name=entity)
            for record in result:
                relations.append(f"{record['e.name']} {record['type(r)']} {record['n.name']}")
    except Exception as e:
        print(f"Neo4j Context Error: {e}")
    finally:
        driver.close()
    return relations

def get_kpis():
    driver = get_driver()
    if not driver: return {"nodes": "0", "edges": "0", "persons": "0", "orgs": "0", "locations": "0"}
    kpis = {"nodes": "0", "edges": "0", "persons": "0", "orgs": "0", "locations": "0"}
    query = """
    MATCH (n) WITH count(n) AS total_nodes
    MATCH ()-[r]->() WITH total_nodes, count(r) AS total_edges
    MATCH (p:PERSON) WITH total_nodes, total_edges, count(p) AS persons
    MATCH (o:ORG) WITH total_nodes, total_edges, persons, count(o) AS orgs
    MATCH (l:LOCATION) RETURN total_nodes, total_edges, persons, orgs, count(l) AS locations
    """
    try:
        with driver.session() as session:
            result = session.run(query)
            record = result.single()
            if record:
                kpis = {
                    "nodes": str(record["total_nodes"]),
                    "edges": str(record["total_edges"]),
                    "persons": str(record["persons"]),
                    "orgs": str(record["orgs"]),
                    "locations": str(record["locations"])
                }
    except Exception as e:
        print(f"Neo4j KPI Error: {e}")
    finally:
        driver.close()
    return kpis

def get_top_entities(label="PERSON", limit=10):
    driver = get_driver()
    if not driver: return []
    clean_label = ''.join(e for e in label if e.isalnum())
    query = f"""
    MATCH (n:{clean_label})-[r:RELATED_TO]-()
    RETURN n.name AS name, count(r) AS degree
    ORDER BY degree DESC LIMIT $limit
    """
    results = []
    try:
        with driver.session() as session:
            result = session.run(query, limit=limit)
            for record in result:
                results.append({"name": record["name"], "connections": record["degree"]})
    except Exception as e:
        print(f"Neo4j Analytics Error: {e}")
    finally:
        driver.close()
    return results

def get_most_connected_nodes(limit=10):
    driver = get_driver()
    if not driver: return []
    query = """
    MATCH (n)-[r:RELATED_TO]-(o)
    RETURN n.name AS name, labels(n)[0] AS label, count(r) AS connections
    ORDER BY connections DESC LIMIT $limit
    """
    results = []
    try:
        with driver.session() as session:
            result = session.run(query, limit=limit)
            for record in result:
                results.append({"name": record["name"], "label": record["label"], "connections": record["connections"]})
    except Exception as e:
        print(f"Neo4j Global Connections Error: {e}")
    finally:
        driver.close()
    return results

def get_top_persons(limit=10):
    return get_top_entities("PERSON", limit)

def get_graph_data_for_visualization(limit=50, filter_label="ALL"):
    driver = get_driver()
    if not driver: return [], []
    
    if filter_label == "ALL":
        query = """
        MATCH (s)-[r:RELATED_TO]->(o)
        RETURN s.name AS source, 
               case when size(labels(s)) > 0 then labels(s)[0] else 'ENTITY' end AS source_label, 
               o.name AS target, 
               case when size(labels(o)) > 0 then labels(o)[0] else 'ENTITY' end AS target_label
        LIMIT $limit
        """
    else:
        clean_label = ''.join(e for e in filter_label if e.isalnum())
        query = f"""
        MATCH (s:{clean_label})-[r:RELATED_TO]-(o)
        RETURN s.name AS source, 
               case when size(labels(s)) > 0 then labels(s)[0] else 'ENTITY' end AS source_label, 
               o.name AS target, 
               case when size(labels(o)) > 0 then labels(o)[0] else 'ENTITY' end AS target_label
        LIMIT $limit
        """
    nodes = set()
    edges = []
    try:
        with driver.session() as session:
            result = session.run(query, limit=limit)
            for record in result:
                src, src_label = record["source"], record["source_label"]
                tgt, tgt_label = record["target"], record["target_label"]
                nodes.add((src, src_label))
                nodes.add((tgt, tgt_label))
                edges.append((src, tgt))
    except Exception as e:
        print(f"Neo4j Visual Error: {e}")
    finally:
        driver.close()
    return list(nodes), edges
