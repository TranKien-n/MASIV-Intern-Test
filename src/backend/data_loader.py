import random
import requests
import os
import json

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
CACHE_FILE = "buildings_cache.json"

OVERPASS_QUERY = """
[out:json][timeout:25];
(
  way["building"](51.0465,-114.0710,51.0495,-114.0665);
);
out body;
>;
out skel qt;
"""


def _estimate_height(tags):
    """
    Estimate building height in meters from OSM tags.

    Priority:
    1. 'height' tag (if numeric and <= 350m)
    2. 'building:levels' * 3.5m (with sanity checks)
    3. Synthetic reasonable default based on building type
    """
    raw_height = tags.get("height")
    raw_levels = tags.get("building:levels")
    height = None

    # 1) Direct height in meters if present and sane
    if raw_height:
        try:
            h = float(str(raw_height).split()[0])
            if 2 <= h <= 350:  # anything above is almost certainly bad data
                height = h
        except Exception:
            pass

    # 2) Convert levels to meters
    if height is None and raw_levels:
        try:
            levels = float(str(raw_levels).split()[0])
            if 1 <= levels <= 120:
                height = levels * 3.5
        except Exception:
            pass

    # 3) Fallback based on building type
    if height is None:
        btype = tags.get("building", "").lower()
        if btype in ("commercial", "office", "retail"):
            height = random.uniform(12, 60)
        elif btype in ("apartments", "residential", "house"):
            height = random.uniform(6, 25)
        else:
            height = random.uniform(8, 35)

    return float(round(height, 1))


def load_buildings():
    print("Requesting OSM buildings from Overpass…")

    data = None

    # 1) Try Overpass
    try:
        resp = requests.post(OVERPASS_URL, data={"data": OVERPASS_QUERY}, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        print("Overpass request succeeded.")
    except Exception as e:
        print("Overpass request failed:", e)

    # 2) If Overpass failed, try to load from local cache
    if data is None:
        if os.path.exists(CACHE_FILE):
            print(f"Loading buildings from cache: {CACHE_FILE}")
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            print("No cache file found. Returning empty building list.")
            return []  # or fallback to some small hardcoded dummy list

    # 3) Normal processing as before (nodes/ways → buildings list)
    elements = data.get("elements", [])
    nodes = {}
    ways = []

    for el in elements:
        if el.get("type") == "node":
            nodes[el["id"]] = (el["lon"], el["lat"])
        elif el.get("type") == "way":
            ways.append(el)

    raw_buildings = []

    for way in ways:
        try:
            node_ids = way.get("nodes", [])
            if len(node_ids) < 3:
                continue

            coords = []
            for nid in node_ids:
                if nid not in nodes:
                    continue
                lon, lat = nodes[nid]
                coords.append((lon, lat))

            if not coords:
                continue
            if coords[0] != coords[-1]:
                coords.append(coords[0])

            tags = way.get("tags", {})
            bid = tags.get("ref") or way.get("id")

            # --- Estimate height realistically ---
            height = _estimate_height(tags)

            # --- Derive a coarse "type" from building tag or zoning ---
            btag = tags.get("building", "").lower()
            if btag in ("commercial", "office", "retail"):
                btype = "commercial"
            elif btag in ("apartments", "residential", "house"):
                btype = "residential"
            else:
                btype = "mixed"

            # --- Simple synthetic zoning from type (for colors & queries) ---
            if btype == "commercial":
                zoning = "C-COR"
            elif btype == "residential":
                zoning = "RC-G"
            else:
                zoning = "MU-1"

            # --- Synthetic value roughly scaled with height ---
            base = 200_000
            value = base + height * random.randint(8_000, 12_000)

            name = tags.get("name")  # may be None, e.g. "The Bow"

            raw_buildings.append(
                {
                    "id": str(bid),
                    "name": name,
                    "height": height,
                    "zoning": zoning,
                    "type": btype,
                    "value": float(round(value)),
                    "footprint": coords,  # lon/lat for now
                }
            )
        except Exception as e:
            print("Skipping way due to error:", e)
            continue

    if not raw_buildings:
        print("No buildings loaded from Overpass.")
        return []

    # Normalize lon/lat → local x,y
    all_lons = [p[0] for b in raw_buildings for p in b["footprint"]]
    all_lats = [p[1] for b in raw_buildings for p in b["footprint"]]
    min_lon = min(all_lons)
    min_lat = min(all_lats)
    SCALE = 10000.0

    buildings = []
    for b in raw_buildings:
        fp_local = [
            [(lon - min_lon) * SCALE, (lat - min_lat) * SCALE]
            for lon, lat in b["footprint"]
        ]
        b["footprint"] = fp_local
        buildings.append(b)

    print(f"Loaded {len(buildings)} buildings from OSM/Overpass")

    # 4) Save to cache for future runs
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(buildings, f)
        print(f"Cached buildings to {CACHE_FILE}")
    except Exception as e:
        print("Failed to write buildings cache:", e)

    return buildings    
