from flask import Flask, jsonify, request, redirect, url_for, render_template_string
import json
import subprocess
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime

app = Flask(__name__)

# File to store price history
PRICE_FILE = "price_history.json"

# Component categories
COMPONENT_CATEGORIES = [
    "Motherboard", "CPU", "GPU", "NVME",
    "CPU Cooler", "Memory", "Case", "Power Supply",
    "Operating System", "Case Fans"
]

# ----------------- Helper functions -----------------

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

# ----------------- Routes -----------------

@app.route("/")
def home():
    return """
    <h2>PC Price Tracker is running</h2>
    <ul>
        <li><a href='/add'>Add Part Numbers</a></li>
        <li><a href='/run_scraper'>Run Scraper Now</a></li>
        <li><a href='/prices'>View Price History (JSON)</a></li>
        <li>View Graph: /graph?component=CPU</li>
    </ul>
    """

# Route to add parts
@app.route("/add", methods=["GET", "POST"])
def add_parts():
    data = load_price_history()
    if request.method == "POST":
        for category in COMPONENT_CATEGORIES:
            part_numbers = request.form.get(category, "")
            if part_numbers:
                # Split by comma and strip spaces
                parts = [p.strip() for p in part_numbers.split(",")]
                for part in parts:
                    if part not in data[category]:
                        data[category][part] = []
        save_price_history(data)
        return redirect(url_for("home"))

    # Render HTML form
    form_html = "<h2>Add Part Numbers</h2><form method='post'>"
    for category in COMPONENT_CATEGORIES:
        form_html += f"<label>{category} (comma separated):</label><br>"
        form_html += f"<input type='text' name='{category}'><br><br>"
    form_html += "<input type='submit' value='Add Parts'></form>"
    return render_template_string(form_html)

# Route to manually run scraper
@app.route("/run_scraper")
def run_scraper():
    try:
        subprocess.Popen(["python", "main.py"])
        return "<h3>Scraper started! It is running in the background.</h3><p><a href='/'>Back Home</a></p>"
    except Exception as e:
        return f"Error starting scraper: {e}"

# Route to view price history JSON
@app.route("/prices")
def prices():
    data = load_price_history()
    return jsonify(data)

# Route to plot price graph for a component
@app.route("/graph")
def graph():
    component = request.args.get("component")
    data = load_price_history()
    if not component or component not in data:
        return f"Component '{component}' not found. Available: {', '.join(COMPONENT_CATEGORIES)}"

    img_data = ""
    plt.figure(figsize=(10,5))
    for part, prices in data[component].items():
        if prices:
            dates = [datetime.strptime(p[0], "%Y-%m-%d %H:%M:%S") for p in prices]
            price_vals = [p[1] for p in prices]
            plt.plot(dates, price_vals, label=part)
    plt.xlabel("Date")
    plt.ylabel("Price (CAD)")
    plt.title(f"{component} Price History")
    plt.legend()
    plt.tight_layout()

    # Convert plot to base64 string to embed in HTML
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    img_data = base64.b64encode(buf.read()).decode()
    plt.close()
    return f"<h2>{component} Price Graph</h2><img src='data:image/png;base64,{img_data}'><p><a href='/'>Back Home</a></p>"

# ----------------- Main -----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
