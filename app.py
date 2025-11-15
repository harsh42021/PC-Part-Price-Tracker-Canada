from flask import Flask, jsonify, request, render_template_string
import json
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime

app = Flask(__name__)

# Supported component categories
COMPONENT_CATEGORIES = [
    "Motherboard",
    "CPU",
    "GPU",
    "NVME",
    "CPU Cooler",
    "Memory",
    "Case",
    "Power Supply",
    "Operating System",
    "Case Fans"
]

# Path to the JSON file storing price history
PRICE_FILE = "price_history.json"

# Load price history from file or initialize empty structure
def load_price_history():
    try:
        with open(PRICE_FILE, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {category: {} for category in COMPONENT_CATEGORIES}
    return data

# Save price history to file
def save_price_history(data):
    with open(PRICE_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Default route
@app.route("/")
def home():
    return "<h2>PC Price Tracker is running</h2><p>Use /prices to see JSON or /graph?component=CPU for graphs.</p>"

# Route to show all prices in JSON
@app.route("/prices")
def prices():
    data = load_price_history()
    return jsonify(data)

# Route to show graph for a single component
@app.route("/graph")
def graph():
    component = request.args.get("component")
    if not component or component not in COMPONENT_CATEGORIES:
        return f"Please provide a valid component in query string, e.g., /graph?component=GPU"

    data = load_price_history()
    component_data = data.get(component, {})

    if not component_data:
        return f"No price history available for {component}"

    # Plot price history for each part number
    plt.figure(figsize=(10,5))
    for part_number, entries in component_data.items():
        dates = [datetime.strptime(e["date"], "%Y-%m-%d %H:%M:%S") for e in entries]
        prices_list = [e["price"] for e in entries]
        plt.plot(dates, prices_list, marker='o', label=part_number)

    plt.title(f"Price history: {component}")
    plt.xlabel("Date")
    plt.ylabel("Price (CAD)")
    plt.legend()
    plt.tight_layout()

    # Convert plot to PNG and embed in HTML
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode()
    buf.close()
    plt.close()

    html = f"""
    <h2>Price History for {component}</h2>
    <img src="data:image/png;base64,{img_base64}"/>
    <p>Use /prices to see raw JSON price data.</p>
    """
    return render_template_string(html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
