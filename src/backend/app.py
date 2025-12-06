from flask import Flask, request, jsonify
from flask_cors import CORS
from data_loader import load_buildings
from llm import interpret_query
from filters import apply_filter

app = Flask(__name__)
CORS(app)  # allow requests from React (localhost:3000)

buildings = load_buildings()

@app.route("/api/buildings", methods=["GET"])
def get_buildings():
    return jsonify(buildings)

@app.route("/api/query", methods=["POST"])
def run_query():
    payload = request.get_json() or {}
    text = payload.get("query", "")

    filt = interpret_query(text)

    # If we couldn't interpret the query (or it's a "reset"),
    # return an empty list of ids.
    if not filt:
        return jsonify({"ids": []})

    ids = apply_filter(buildings, filt)

    # Always return an object with an "ids" field.
    return jsonify({"ids": ids})



if __name__ == "__main__":
    app.run(debug=True)
