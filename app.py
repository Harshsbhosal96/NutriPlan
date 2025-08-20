from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import os
from clustering import perform_clustering

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/plan')
def plan():
    return render_template('plan.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/cluster')
def cluster_page():
    return render_template('cluster.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'excel-file' not in request.files:
        return "No file part"
    file = request.files['excel-file']
    if file.filename == '':
        return "No selected file"
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    clusters, charts = perform_clustering(filepath)
    return render_template('results.html', clusters=clusters, charts=charts)

@app.route('/generate-plan', methods=['POST'])
def generate_plan():
    data = request.get_json()
    print("Received data:", data)

    # Extract required fields
    hemoglobin = float(data.get('hemoglobin', 0))
    vitamin_d = float(data.get('vitamin_d', 0))
    calcium = float(data.get('calcium', 0))

    # --- Determine cluster ---
    if hemoglobin > 13 and vitamin_d > 30 and calcium > 9:
        cluster = "Cluster 1 (Healthy)"
    elif (10 < hemoglobin <= 13) or (20 < vitamin_d <= 30) or (7 < calcium <= 9):
        cluster = "Cluster 2 (Mild Deficiency)"
    else:
        cluster = "Cluster 3 (Severe Deficiency)"

    # --- Determine deficiency ---
    if hemoglobin < 12:
        deficiency = "Iron Deficiency Suspected"
    elif vitamin_d < 20:
        deficiency = "Vitamin D Deficiency"
    elif calcium < 8:
        deficiency = "Calcium Deficiency"
    else:
        deficiency = "No deficiency detected"

    # --- Determine anomaly (optional: simple) ---
    anomaly = "No sudden changes detected"  # You can add logic here if needed

    # --- Fixed meal plans ---
    meal_plan_mapping = {
        "Cluster 1 (Healthy)": [
            {"meal": "Breakfast", "food": "Idli with sambar, banana", "portion": "2 idlis + 1 banana"},
            {"meal": "Lunch",     "food": "Rice, dal, spinach sabzi", "portion": "1 cup each"},
            {"meal": "Snack",     "food": "Boiled egg / Chana", "portion": "1 egg / 1 cup chana"},
            {"meal": "Dinner",    "food": "Chapati, mixed veg curry", "portion": "2 chapatis + 1 cup curry"}
        ],
        "Cluster 2 (Mild Deficiency)": [
            {"meal": "Breakfast", "food": "Poha with peanuts", "portion": "1 plate"},
            {"meal": "Lunch",     "food": "Jeera rice, rajma", "portion": "1 bowl each"},
            {"meal": "Snack",     "food": "Fruit salad", "portion": "1 bowl"},
            {"meal": "Dinner",    "food": "Vegetable khichdi", "portion": "1 bowl"}
        ],
        "Cluster 3 (Severe Deficiency)": [
            {"meal": "Breakfast", "food": "Upma with coconut chutney", "portion": "1 bowl"},
            {"meal": "Lunch",     "food": "Roti, methi sabzi, curd", "portion": "2 rotis + 1 cup sabzi + 1 cup curd"},
            {"meal": "Snack",     "food": "Sprouts chaat", "portion": "1 bowl"},
            {"meal": "Dinner",    "food": "Vegetable pulao", "portion": "1.5 cups"}
        ]
    }

    meal_plan = meal_plan_mapping[cluster]

    return jsonify({
        "cluster": cluster,
        "deficiency": deficiency,
        "anomaly": anomaly,
        "meal_plan": meal_plan
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

