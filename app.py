from flask import Flask, jsonify, request, render_template_string, redirect, url_for
import subprocess
import json
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime

app = Flask(__name__)

COMPONENT_CATEGORIES = [
    "Motherboard", "CPU", "GPU", "NVME", "CPU Cooler",
    "Memory", "Case", "Power Supply", "Operating System", "Case Fans"
]

PRICE_FILE = "price_history.json"

def load_price_history():
    try:
        with open(PRICE_FILE, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {category: {} for category in COMPONENT_CATEGORIES}
    return data

def save_price_history(data):
    with open(PRICE_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/")
def home():
    return """
    <h2>PC Price Tracker is running</h2>
    <p>Use /prices to see JSON or /graph?component=CPU for graphs.</p>
    <p>Use <a href='/add'>/add</a> to add part numbers for tracking.</p>
    <p>Use <a href='/run_scraper'>Run Scraper Now</a> to update prices manually.</p>
    """

@app.route("/run_scraper")
def run_scraper():
    try:
        subprocess.Popen(["python", "main.py"])
        return "<h3>Scraper started! It is running in the background.</h3><p><a href='/'>Back Home</a></p>"
    except Exception as e:
        return f"Error starting scraper: {e}"

# Graph and add parts routes remain the same as previous app.py
# ... (keep /graph and /add routes as we did before)
