from flask import Flask, jsonify
import json

app = Flask(__name__)

@app.route('/')
def home():
    return "PC Price Tracker is running"

@app.route('/prices')
def prices():
    try:
        with open('price_history.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
