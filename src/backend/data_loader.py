import random
import os
import json

CACHE_FILE = os.path.join(os.path.dirname(__file__), "buildings_cache.json")


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
    """
    Deployment-safe loader: load buildings ONLY from a local cache file.

    This avoids calling Overpass at startup (which can be slow or blocked
    on Render). The cache should be generated locally and committed as
    'buildings_cache.json' in the backend directory.
    """
    if os.path.exists(CACHE_FILE):
        print(f"[data_loader] Loading buildings from cache: {CACHE_FILE}")
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[data_loader] ERROR reading cache: {e}")
            return []

    print("[data_loader] WARNING: No cache file found at", CACHE_FILE)
    print("[data_loader] Returning empty building list.")
    return []    
