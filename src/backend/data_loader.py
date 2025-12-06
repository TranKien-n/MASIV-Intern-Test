"""
Building data loader.

In deployment, we avoid live Overpass queries and instead load buildings from
a pre-generated JSON cache file (`buildings_cache.json`) committed to the repo.

This keeps startup fast and avoids rate limits or network failures.
"""

import os
import json
import random

CACHE_FILE = os.path.join(os.path.dirname(__file__), "buildings_cache.json")


def _estimate_height(tags):
    """
    Estimate building height in meters from OSM-like tags.

    Priority:
      1. 'height' tag (if numeric and <= 350m)
      2. 'building:levels' * 3.5m (with sanity checks)
      3. Synthetic fallback range based on coarse building type
    """
    raw_height = tags.get("height")
    raw_levels = tags.get("building:levels")
    height = None

    # 1. Direct numeric height in meters, with sanity cap.
    if raw_height:
        try:
            h = float(str(raw_height).split()[0])
            if 2 <= h <= 350:
                height = h
        except Exception:
            pass

    # 2. Derive from number of levels.
    if height is None and raw_levels:
        try:
            levels = float(str(raw_levels).split()[0])
            if 1 <= levels <= 120:
                height = levels * 3.5
        except Exception:
            pass

    # 3. Synthetic fallback based on building type.
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
    Load buildings from a local cache file.

    The cache should contain a list of building dicts in the format expected
    by the frontend (id, name, height, zoning, type, value, footprint).

    Returns:
        list[dict]: list of building objects, or [] if none could be loaded.
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
