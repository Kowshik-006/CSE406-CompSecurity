from flask import Flask, send_from_directory, request, jsonify
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import torch
import torch.nn as nn
import json
from train import FingerprintClassifier, ComplexFingerprintClassifier
# additional imports

app = Flask(__name__)

# -- Model Loading and Preprocessing --
# Configuration from train.py
INPUT_SIZE = 1000
HIDDEN_SIZE = 128
DATASET_PATH = "dataset_merged_2.json"
MODEL_NAME = "simple"  # Choose 'simple' or 'complex'

# Load website names and get num_classes from the dataset
with open(DATASET_PATH, 'r') as f:
    data = json.load(f)

# Create a mapping from index to website name
index_to_website = {item['website_index']: item['website'] for item in data}
websites = [index_to_website[i] for i in sorted(index_to_website.keys())]
num_classes = len(websites)

# Initialize and load the model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

if MODEL_NAME == 'simple':
    model = FingerprintClassifier(INPUT_SIZE, HIDDEN_SIZE, num_classes)
    model_path = "saved_models/simple_model.pth"
elif MODEL_NAME == 'complex':
    model = ComplexFingerprintClassifier(INPUT_SIZE, HIDDEN_SIZE, num_classes)
    model_path = "saved_models/complex_model.pth"
else:
    raise ValueError("Invalid MODEL_NAME specified. Choose 'simple' or 'complex'.")
    
model.load_state_dict(torch.load(model_path, map_location=device))
model.to(device)
model.eval()

# Helper function for preprocessing
def preprocess_trace(trace_data):
    # Pad or truncate to INPUT_SIZE
    if len(trace_data) > INPUT_SIZE:
        trace_data = trace_data[:INPUT_SIZE]
    else:
        trace_data = np.pad(trace_data, (0, INPUT_SIZE - len(trace_data)), 'constant')

    trace = np.array(trace_data, dtype=np.float32)
    trace = (trace - np.mean(trace)) / (np.std(trace) + 1e-8) # Normalization
    return torch.FloatTensor(trace).unsqueeze(0).to(device)

stored_traces = []
stored_heatmaps = []

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

@app.route('/collect_trace', methods=['POST'])
def collect_trace():
    """ 
    Implement the collect_trace endpoint to receive trace data from the frontend and generate a heatmap.
    1. Receive trace data from the frontend as JSON
    2. Generate a heatmap using matplotlib
    3. Store the heatmap and trace data in the backend temporarily
    4. Return the heatmap image and optionally other statistics to the frontend
    """
    # 1. Receive trace data from the frontend as JSON
    trace_data = request.get_json()
    if not isinstance(trace_data, list):
        return jsonify({'error': 'trace_data must be a list'}), 400

    # Prediction
    preprocessed_trace = preprocess_trace(trace_data)
    with torch.no_grad():
        output = model(preprocessed_trace)
        _, predicted_idx = torch.max(output.data, 1)
        predicted_website = websites[predicted_idx.item()]

    # 2. Generate a heatmap using matplotlib
    arr = np.array(trace_data).reshape(1, -1)  # 1 row, N columns
    plt.figure(figsize=(10, 1.2))
    plt.imshow(arr, aspect='auto', cmap='plasma')
    plt.axis('off')  # Hide axes for a clean look
    plt.tight_layout(pad=0)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    buf.seek(0)
    plt.close()

    # 3. Store the heatmap and trace data in the backend temporarily
    stored_traces.append(trace_data)
    stored_heatmaps.append(buf.getvalue())

    # 4. Return the heatmap image and optionally other statistics to the frontend
    heatmap_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    min_count = int(np.min(arr))
    max_count = int(np.max(arr))
    range_count = max_count - min_count
    samples = len(trace_data)
    stats = {
        'min': min_count,
        'max': max_count,
        'range': range_count,
        'samples': samples
    }
    return jsonify({
        'heatmap': heatmap_base64,
        'statistics': stats,
        'prediction': predicted_website
    })

@app.route('/api/clear_results', methods=['POST'])
def clear_results():
    """ 
    Implement a clear results endpoint to reset stored data.
    1. Clear stored traces and heatmaps
    2. Return success/error message
    """
    stored_traces.clear()
    stored_heatmaps.clear()
    return jsonify({'message': 'Results cleared successfully'})

@app.route('/api/get_results', methods=['GET'])
def get_results():
    """
    Implement the get_results endpoint to return stored traces.
    1. Return all stored traces in a format suitable for the frontend
    2. Return empty list if no traces are stored
    """
    return jsonify({
        'traces': stored_traces
    })

# Additional endpoints can be implemented here as needed.

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)