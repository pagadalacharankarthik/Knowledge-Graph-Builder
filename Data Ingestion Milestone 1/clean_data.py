import re

def clean_email(text):
    text = str(text)
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^A-Za-z ]', '', text)
    return text.lower()

def apply_cleaning(df):
    df['clean_message'] = df['message'].apply(clean_email)
    return df
