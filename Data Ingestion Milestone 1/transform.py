def transform_data(df):
    df['word_count'] = df['clean_message'].apply(lambda x: len(str(x).split()))
    return df
