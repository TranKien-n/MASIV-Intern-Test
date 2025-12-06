from typing import List, Dict, Any


def _get_numeric(b: Dict[str, Any], attr: str):
  """
  Safely get a numeric attribute (height, value, etc.) as float.
  Returns None if missing / not convertible.
  """
  v = b.get(attr)
  if v is None:
    return None
  try:
    return float(v)
  except (TypeError, ValueError):
    return None


def _matches_numeric(b: Dict[str, Any], attr: str, op: str, value):
  """
  Generic numeric comparison: >, <, BETWEEN
  """
  x = _get_numeric(b, attr)
  if x is None:
    return False

  if op == ">":
    return x > float(value)
  if op == "<":
    return x < float(value)
  if op == "BETWEEN":
    low, high = value
    return low <= x <= high

  return False


def _matches_equality(b: Dict[str, Any], attr: str, value: str):
  """
  Simple case-insensitive equality for zoning/type, etc.
  """
  v = b.get(attr)
  if v is None:
    return False
  return str(v).strip().lower() == str(value).strip().lower()


def apply_filter(buildings: List[Dict[str, Any]], filt: Dict[str, Any]) -> List[str]:
  """
  Apply a structured filter to the list of buildings and return a list of IDs.

  filt is expected to be:
    {
      "attribute": "height" | "value" | "zoning" | "type",
      "operator": ">" | "<" | "=" | "BETWEEN" | "TOP" | "BOTTOM",
      "value": number | string | [low, high]
    }
  """
  if not filt:
    return []

  attr = filt.get("attribute")
  op = filt.get("operator")
  val = filt.get("value")

  if not attr or not op:
    return []

  # --- TOP / BOTTOM k for numeric attributes ---
  if op in ("TOP", "BOTTOM"):
    # fallback to 1 if something weird happens
    try:
      k = int(val)
    except (TypeError, ValueError):
      k = 1

    # collect numeric values
    scored = []
    for b in buildings:
      x = _get_numeric(b, attr)
      if x is not None:
        scored.append((x, b.get("id")))

    if not scored:
      return []

    # sort descending for TOP (largest first), ascending for BOTTOM
    scored.sort(key=lambda t: t[0], reverse=(op == "TOP"))

    # take first k
    top_k = scored[:k]
    ids = [bid for (_, bid) in top_k if bid is not None]
    return ids

  # --- Equality for zoning / type ---
  if op == "=":
    ids = []
    for b in buildings:
      if _matches_equality(b, attr, val):
        bid = b.get("id")
        if bid is not None:
          ids.append(bid)
    return ids

  # --- Numeric comparisons (> , < , BETWEEN) ---
  if op in (">", "<", "BETWEEN"):
    ids = []
    for b in buildings:
      if _matches_numeric(b, attr, op, val):
        bid = b.get("id")
        if bid is not None:
          ids.append(bid)
    return ids

  # Unknown operator: no matches
  return []
