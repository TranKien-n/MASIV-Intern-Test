from flask import Flask, request, jsonify
from data_loader import load_buildings
from llm import interpret_query
from filters import apply_filter

app = Flask(__name__)

# Load buildings once at startup
buildings = load_buildings()

@app.route("/api/buildings")
def get_buildings():
    return jsonify(buildings)

@app.route("/api/query", methods=["POST"])
def query():
    user_query = request.json.get("query", "")
    filter_obj = interpret_query(user_query)
    filtered_ids = apply_filter(buildings, filter_obj)
    return jsonify({"filtered_ids": filtered_ids})

if __name__ == "__main__":
    app.run(debug=True)
