from load_data import load_data
from clean_data import apply_cleaning
from transform import transform_data
from enrich import enrich_data

df = load_data()
df = apply_cleaning(df)
df = transform_data(df)
df = enrich_data(df)

df = df[['message', 'clean_message', 'word_count', 'entities']]
df.to_csv("cleaned_enron_emails.csv", index=False)

print("Milestone 1 completed")
