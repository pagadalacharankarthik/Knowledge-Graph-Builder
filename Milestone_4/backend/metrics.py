import os
import csv
import json
from datetime import datetime

# Fallback mechanism: use CSV for metrics
METRICS_FILE = os.path.join(os.path.dirname(__file__), 'metrics_log.csv')

def init_metrics_file():
    """Ensure the metrics CSV file exists with the right headers."""
    headers = [
        "timestamp", 
        "query", 
        "response_time", 
        "similarity_score", 
        "retrieved_docs_count", 
        "answer_length",
        "approx_accuracy"
    ]
    if not os.path.exists(METRICS_FILE):
        try:
            with open(METRICS_FILE, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
        except Exception as e:
            print(f"Error creating metrics file: {e}")

def log_metrics(metrics_data):
    """
    Logs metrics data. 
    Expects a dict with: query, response_time, similarity_score, retrieved_docs_count, answer_length
    """
    init_metrics_file()
    
    timestamp = datetime.now().isoformat()
    query = metrics_data.get("query", "")
    response_time = round(metrics_data.get("response_time", 0.0), 3)
    similarity_score = round(metrics_data.get("similarity_score", 0.0), 4)
    retrieved_docs_count = metrics_data.get("retrieved_docs_count", 0)
    answer_length = metrics_data.get("answer_length", 0)
    
    # Calculate approx accuracy based on similarity score (proxy)
    # Using L2 distance from FAISS, lower distance = higher similarity
    # We map distance to a 0-100% scale proxy roughly. Assuming distance < 1 is great, > 2 is poor.
    # This is a heuristic proxy.
    approx_accuracy = 100
    if similarity_score > 0:
        # e.g., mapping distance to percentage: 100 - (distance * 10) capped at 0-100
        approx_accuracy = max(0, min(100, int(100 - (similarity_score * 30))))
    
    row = [
        timestamp,
        query,
        response_time,
        similarity_score,
        retrieved_docs_count,
        answer_length,
        approx_accuracy
    ]
    
    try:
        with open(METRICS_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row)
    except Exception as e:
        print(f"Error logging metrics: {e}")

def load_metrics():
    """Reads the metrics CSV and returns a list of dictionaries for pandas."""
    if not os.path.exists(METRICS_FILE):
        return []
    
    data = []
    try:
        with open(METRICS_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert types
                row['response_time'] = float(row.get('response_time', 0))
                row['similarity_score'] = float(row.get('similarity_score', 0))
                row['retrieved_docs_count'] = int(row.get('retrieved_docs_count', 0))
                row['answer_length'] = int(row.get('answer_length', 0))
                row['approx_accuracy'] = float(row.get('approx_accuracy', 0))
                data.append(row)
    except Exception as e:
        print(f"Error reading metrics: {e}")
    return data

def build_daily_summary():
    """Generates a daily summary from the metrics log and prints/saves it."""
    metrics = load_metrics()
    if not metrics:
        return "No metrics available today."
        
    today = datetime.now().date().isoformat()
    today_metrics = [m for m in metrics if m['timestamp'].startswith(today)]
    
    if not today_metrics:
        return f"No metrics for {today}."
        
    total_queries = len(today_metrics)
    avg_response_time = sum(float(m['response_time']) for m in today_metrics) / total_queries
    avg_accuracy = sum(float(m['approx_accuracy']) for m in today_metrics) / total_queries
    
    summary = (
        f"--- DAILY METRICS SUMMARY: {today} ---\n"
        f"Total Queries: {total_queries}\n"
        f"Average Response Time: {avg_response_time:.2f}s\n"
        f"Average Approx Accuracy: {avg_accuracy:.1f}%\n"
        "--------------------------------------\n"
    )
    
    # Save summary file
    summary_path = os.path.join(os.path.dirname(__file__), f"summary_{today}.txt")
    try:
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Daily summary saved to {summary_path}")
    except Exception as e:
        print(f"Failed to save summary: {e}")
        
    return summary
