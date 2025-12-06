import requests
import os

HF_API_KEY = os.getenv("HF_API_KEY")

def interpret_query(query):
    prompt = f"""
    Extract a filter from this natural language request:
    "{query}"
    Return JSON with keys: attribute, operator, value.
    Example: {{ "attribute": "height", "operator": ">", "value": 100 }}
    """

    response = requests.post(
        "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct",
        headers={"Authorization": f"Bearer {HF_API_KEY}"},
        json={"inputs": prompt}
    )

    try:
        return response.json()
    except:
        return {"attribute": "height", "operator": ">", "value": 0}
