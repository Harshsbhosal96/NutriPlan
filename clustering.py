# clustering.py

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest

def perform_clustering(filepath):
    # 1) Read spreadsheet (support .xlsx or .csv)
    if filepath.endswith('.csv'):
        df = pd.read_csv(filepath)
    else:
        df = pd.read_excel(filepath, engine='openpyxl')

    # 2) Keep a copy of original student info
    output = df.copy()

    # 3) Features for clustering & anomaly detection
    features = ['Age', 'Weight', 'Height', 'Hemoglobin', 'MUAC']
    X = df[features].fillna(df[features].mean())

    # 4) K-Means clustering (3 groups)
    kmeans = KMeans(n_clusters=3, random_state=42)
    output['Cluster'] = kmeans.fit_predict(X)

    # 5) Simple deficiency rules
    def detect_deficiency(row):
        flags = []
        if row['Hemoglobin'] < 11.0:
            flags.append('Anemia')
        if row['Weight'] < 15.0:  
            flags.append('Underweight')
        return ', '.join(flags) if flags else 'None'

    output['Deficiency'] = output.apply(detect_deficiency, axis=1)

    # 6) Anomaly detection
    iso = IsolationForest(contamination=0.05, random_state=42)
    preds = iso.fit_predict(X)
    output['Anomaly'] = preds.tolist()
    # map 1 → 'No', -1 → 'Yes'
    output['Anomaly'] = output['Anomaly'].map({1: 'No', -1: 'Yes'})

    # 7) Convert to list of dicts for rendering
    return output.to_dict(orient='records')
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
import io
import base64

def perform_clustering(filepath):
    # 1) Read spreadsheet (support .xlsx or .csv)
    if filepath.endswith('.csv'):
        df = pd.read_csv(filepath)
    else:
        df = pd.read_excel(filepath, engine='openpyxl')

    # 2) Keep a copy of original student info
    output = df.copy()

    # 3) Features for clustering & anomaly detection
    features = ['Age', 'Weight', 'Height', 'Hemoglobin', 'MUAC']
    X = df[features].fillna(df[features].mean())

    # 4) K-Means clustering (3 groups)
    kmeans = KMeans(n_clusters=3, random_state=42)
    output['Cluster'] = kmeans.fit_predict(X)

    # 5) Simple deficiency rules
    def detect_deficiency(row):
        flags = []
        if row['Hemoglobin'] < 11.0:
            flags.append('Anemia')
        if row['Weight'] < 15.0:  
            flags.append('Underweight')
        return ', '.join(flags) if flags else 'None'

    output['Deficiency'] = output.apply(detect_deficiency, axis=1)

    # 6) Anomaly detection
    iso = IsolationForest(contamination=0.05, random_state=42)
    preds = iso.fit_predict(X)
    output['Anomaly'] = preds.tolist()
    output['Anomaly'] = output['Anomaly'].map({1: 'No', -1: 'Yes'})

    # 7) Charts to visualize clustering
    charts = []

    # a) Cluster distribution bar chart
    plt.figure(figsize=(6, 4))
    output['Cluster'].value_counts().sort_index().plot(kind='bar', color=['skyblue', 'lightgreen', 'salmon'])
    plt.title("Cluster Distribution")
    plt.xlabel("Cluster")
    plt.ylabel("Number of Students")
    charts.append(get_base64_plot())

    # b) Scatter: Weight vs Height
    plt.figure(figsize=(6, 4))
    for cluster in output['Cluster'].unique():
        subset = output[output['Cluster'] == cluster]
        plt.scatter(subset['Weight'], subset['Height'], label=f"Cluster {cluster}")
    plt.title("Weight vs Height by Cluster")
    plt.xlabel("Weight")
    plt.ylabel("Height")
    plt.legend()
    charts.append(get_base64_plot())

    # c) Scatter: MUAC vs Hemoglobin
    plt.figure(figsize=(6, 4))
    for cluster in output['Cluster'].unique():
        subset = output[output['Cluster'] == cluster]
        plt.scatter(subset['MUAC'], subset['Hemoglobin'], label=f"Cluster {cluster}")
    plt.title("MUAC vs Hemoglobin by Cluster")
    plt.xlabel("MUAC")
    plt.ylabel("Hemoglobin")
    plt.legend()
    charts.append(get_base64_plot())

    # 8) Return both table data and chart images
    return output.to_dict(orient='records'), charts

def get_base64_plot():
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')
