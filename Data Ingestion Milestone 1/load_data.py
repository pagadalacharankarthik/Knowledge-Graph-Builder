from datasets import load_dataset
import pandas as pd

def load_data():
    # Use streaming=True to fetch samples without downloading the whole dataset
    dataset = load_dataset("corbt/enron-emails", streaming=True)
    train_stream = dataset['train']
    
    # Take first 10000 real emails for high accuracy and safe file size
    data_list = []
    print("Streaming 10,000 emails...")
    for i, item in enumerate(train_stream):
        data_list.append(item)
        if i >= 9999: break
        
    df = pd.DataFrame(data_list)
    # Rename 'body' to 'message' if it exists to match MS1 expectation
    if 'body' in df.columns:
        df = df.rename(columns={'body': 'message'})
    return df
