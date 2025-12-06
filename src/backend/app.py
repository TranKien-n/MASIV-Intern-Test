import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from data_loader import load_buildings
from llm import interpret_query
from filters import apply_filter

app = Flask(__name__)
CORS(app)

buildings = load_buildings()

@app.route("/api/buildings", methods=["GET"])
def get_buildings():
    return jsonify(buildings)

@app.route("/api/query", methods=["POST"])
def run_query():
    payload = request.get_json() or {}
    text = payload.get("query", "")

    filt = interpret_query(text)
    if not filt:
        # consistent frontend contract: always return ids + filter
        return jsonify({"ids": [], "filter": None})

    ids = apply_filter(buildings, filt)
    return jsonify({"ids": ids, "filter": filt})

# 🔹 Add a simple health-check route so HEAD / returns 200 instead of 404
@app.route("/", methods=["GET", "HEAD"])
def health():
    return "Backend is running", 200


if __name__ == "__main__":
    # 🔹 IMPORTANT for Render: bind to 0.0.0.0 and use $PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
