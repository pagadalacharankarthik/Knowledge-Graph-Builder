# 📌 Milestone 2: Knowledge Graph Construction from Enron Emails

## 📖 Overview
Milestone 2 focuses on transforming unstructured email data into a structured **Knowledge Graph**.  
Using NLP techniques, entities and relationships are extracted from the Enron Email Dataset and stored in a graph database for advanced querying and analysis.

---

## 🎯 Objective
- Extract entities: **Person, Organization, Location, Date**
- Identify relationships between entities
- Construct a scalable knowledge graph
- Enable graph-based queries and insights

---

## ⚙️ Technologies Used
- Python
- SpaCy (NER)
- Pandas
- Neo4j
- Fuzzy Matching (Entity Canonicalization)

---

## 🧩 Workflow

### 1. Data Preprocessing
- Load cleaned dataset (`cleaned_enron_emails.csv`)
- Remove noise (emails, URLs, unwanted text)
- Normalize text

---

### 2. Entity Extraction
Use SpaCy to extract:
- `PERSON`
- `ORG`
- `LOCATION`
- `DATE`

---

### 3. Entity Refinement
- Remove noisy entities (short words, irrelevant tokens)
- Apply canonicalization  
  - Example: `"P. Allen"` → `"Phillip Allen"`

---

### 4. Relationship Extraction
- Generate relationships using **co-occurrence logic**
- Create triples:


(Entity1) — RELATED_TO → (Entity2)


---

### 5. Graph Construction
- Insert nodes into Neo4j with dynamic labels:
  - `:PERSON`
  - `:ORG`
  - `:LOCATION`
  - `:DATE`

- Create relationships:
  - `:RELATED_TO`

---

### 6. Indexing
- Create indexes on entity names for faster queries

---

### 7. Validation
Ensure:
- No duplicate or noisy entities
- Correct number of nodes and relationships
- No generic or invalid labels

---

## 📊 Example Queries

### Get sample persons
cypher
- MATCH (p:PERSON) RETURN p.name LIMIT 10;

## Top relationships by weight
``MATCH (a:PERSON)-[r:RELATED_TO]-(b:PERSON)
RETURN a.name, b.name, r.weight
ORDER BY r.weight DESC
LIMIT 5;``

## 📁 Outputs
- Structured Knowledge Graph in Neo4j
- Node Types:
  - PERSON
  - ORG
  - LOCATION
  - DATE
- Relationship:
  - RELATED_TO

## ⚠️ Challenges
- Noisy entity extraction
- Duplicate entities
- Inconsistent naming

## ✅ Solutions
- Entity filtering rules
- Canonicalization using fuzzy matching
- Dynamic labeling in Neo4j

## 🚀 Outcome
- Built a clean and queryable knowledge graph
- Enabled relationship discovery between entities
- Improved data exploration through graph queries
