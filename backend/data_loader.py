import requests

CALGARY_DATA_URL = "https://data.calgary.ca/resource/your_dataset_here.json?$limit=2000"

def load_buildings():
    response = requests.get(CALGARY_DATA_URL).json()
    buildings = []

    for b in response:
        try:
            footprint = b.get("the_geom", {}).get("coordinates", [[]])[0]
            buildings.append({
                "id": b.get("building_id", b.get("id")),
                "height": float(b.get("height", 10)),
                "zoning": b.get("zoning", "Unknown"),
                "value": float(b.get("assessed_value", 0)),
                "footprint": footprint
            })
        except:
            continue

    return buildings
