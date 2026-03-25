
def extract_entities(text):
    # Simple dummy entity extraction: words that start with a capital letter
    words = str(text).split()
    ents = [(w, 'PERSON') for w in words if w[0].isupper() and len(w) > 1]
    return str(ents[:10])

def enrich_data(df):
    df['entities'] = df['clean_message'].apply(extract_entities)
    return df
