"""
Flask backend for the MASIV 3D Calgary City Dashboard.

Exposes:
- GET /api/buildings : return all buildings as JSON
- POST /api/query    : run a natural-language query, return matching IDs + filter
- GET /             : simple health check for hosting platforms
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS

from data_loader import load_buildings
from llm import interpret_query
from filters import apply_filter

app = Flask(__name__)
CORS(app)

# Load building data once at startup. In production this is served
# from a pre-generated cache file (see data_loader.load_buildings).
buildings = load_buildings()


@app.route("/api/buildings", methods=["GET"])
def get_buildings():
    """
    Return the full list of buildings as JSON.

    The frontend uses this to build the 3D scene.
    """
    return jsonify(buildings)


@app.route("/api/query", methods=["POST"])
def run_query():
    """
    Run a natural-language query against the building dataset.

    Expected request JSON:
      { "query": "<user text>" }

    Response JSON:
      {
        "ids": ["id1", "id2", ...],  # matching building IDs
        "filter": { ... } or null    # parsed filter for debug / UI
      }
    """
    payload = request.get_json() or {}
    text = payload.get("query", "")

    # First try the hybrid interpreter (LLM + rule-based).
    filt = interpret_query(text)

    # Always return a consistent shape so the frontend can rely on it.
    if not filt:
        return jsonify({"ids": [], "filter": None})

    ids = apply_filter(buildings, filt)
    return jsonify({"ids": ids, "filter": filt})


@app.route("/", methods=["GET", "HEAD"])
def health():
    """
    Lightweight health-check endpoint used by some hosting platforms.
    """
    return "Backend is running", 200


if __name__ == "__main__":
    # For local development we default to port 5000,
    # while platforms like Render provide $PORT.
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
