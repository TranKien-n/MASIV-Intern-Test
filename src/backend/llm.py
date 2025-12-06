# Translate a natural language query into a simple filter dictionary:
#   {"attribute": "height" | "value" | "zoning" | "type",
#    "operator": ">" | "<" | "=" | "BETWEEN" | "TOP" | "BOTTOM",
#    "value": number | string | [low, high]}

import re
import os
import json
import requests

# --------------------------------------------------------------------
# Hugging Face Inference API configuration
# --------------------------------------------------------------------
HF_API_KEY = os.getenv("HF_API_KEY")  # set this in env (local + Render)
HF_MODEL_ID = os.getenv("HF_MODEL_ID", "mistralai/Mixtral-8x7B-Instruct")
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL_ID}"

HEIGHT_KEYWORDS = (
    "height", "tall", "taller", "tallest", "short", "shorter",
    "storeys", "stories", "levels", "floor", "floors",
    "feet", "foot", "ft", "meter", "metre", "m"
)

VALUE_KEYWORDS = (
    "value", "worth", "price", "cost", "expensive", "cheap",
    "cheaper", "cheapest", "priciest", "most expensive", "least expensive",
    "assessment", "assessed", "dollar", "dollars", "usd"
)

ZONING_KEYWORDS = (
    "zoning", "zone", "rc-", "c-", "mu-", "residential", "commercial", "mixed"
)

RESET_KEYWORDS = ("reset", "clear", "show all", "all buildings")

ORDINAL_WORDS = {
    "first": 1,
    "second": 2,
    "third": 3,
    "fourth": 4,
    "fifth": 5,
    "sixth": 6,
    "seventh": 7,
    "eighth": 8,
    "ninth": 9,
    "tenth": 10,
}


def _to_float(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def _guess_attribute(q_lower: str, original: str) -> str:
    """
    Decide whether the user is talking about height, value, or zoning.
    """
    if any(k in q_lower for k in HEIGHT_KEYWORDS):
        return "height"
    # If they mention money words OR use a '$', assume value
    if any(k in q_lower for k in VALUE_KEYWORDS) or "$" in original:
        return "value"
    if any(k in q_lower for k in ZONING_KEYWORDS):
        # could be type or zoning; we keep zoning because we map types to codes
        return "zoning"
    # Default attribute (matches assignment example "over 100 feet")
    return "height"


def _convert_units(q_lower: str, number: float) -> float:
    """
    Convert number to meters for height queries.
    - If query mentions feet/ft, convert feet -> meters
    - If query mentions meters/m, keep as-is
    For value queries we assume the number is already in dollars.
    """
    if "feet" in q_lower or "foot" in q_lower or "ft" in q_lower:
        # 1 foot = 0.3048 m
        return number * 0.3048
    # default: keep number as is
    return number


def _match_ordinal(q_lower: str):
    """
    Return an integer ordinal (2 for 'second', 3 for '3rd', etc.)
    or None if no ordinal is found.
    """
    # word ordinals: "second", "third", ...
    for word, n in ORDINAL_WORDS.items():
        if word in q_lower:
            return n

    # numeric ordinals: "2nd", "3rd", "4th"
    m = re.search(r"\b(\d+)(st|nd|rd|th)\b", q_lower)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            return None

    return None


# --------------------------------------------------------------------
# RULE-BASED INTERPRETER (your original logic)
# --------------------------------------------------------------------
def _interpret_rule_based(query: str):
    """
    Your existing deterministic interpreter.
    """
    if not query or not query.strip():
        return None

    q_raw = query.strip()
    q_lower = q_raw.lower()
    # Remove currency symbols and commas so "$1,000,000" -> "1000000"
    q_clean = q_lower.replace("$", "").replace(",", "")

    # --- Reset / show all ---
    if any(kw in q_lower for kw in RESET_KEYWORDS):
        return None

    # --- Ordinal-based ranking: "second tallest", "3rd most expensive" ---
    ordinal = _match_ordinal(q_lower)
    if ordinal is not None:
        # Height-based: "second tallest", "3rd highest building"
        if "tallest" in q_lower or "highest" in q_lower or "tall" in q_lower:
            return {
                "attribute": "height",
                "operator": "TOP",
                "value": ordinal,  # highlight top N, where N is the ordinal
            }

        # Value-based: "second most expensive", "3rd priciest"
        if "most expensive" in q_lower or "priciest" in q_lower or "highest value" in q_lower:
            return {
                "attribute": "value",
                "operator": "TOP",
                "value": ordinal,
            }

        # Value-based, bottom: "second cheapest", "3rd least expensive"
        if "cheapest" in q_lower or "least expensive" in q_lower or "lowest value" in q_lower:
            return {
                "attribute": "value",
                "operator": "BOTTOM",
                "value": ordinal,
            }

        # Height-based, bottom: "second shortest", "3rd lowest building"
        if "shortest" in q_lower or "lowest building" in q_lower or "short" in q_lower:
            return {
                "attribute": "height",
                "operator": "BOTTOM",
                "value": ordinal,
            }

    # --- Special TOP/BOTTOM intents (non-ordinal numeric) ---

    # Highest / tallest building(s)
    if "highest" in q_lower or "tallest" in q_lower:
        # e.g. "highest building", "highlight tallest 3 buildings"
        m = re.search(r"(?:highest|tallest)\s+(\d+)", q_clean)
        k = 1
        if m:
            k = int(m.group(1))
        return {"attribute": "height", "operator": "TOP", "value": k}

    # Shortest / lowest building(s)
    if "shortest" in q_lower or "lowest building" in q_lower:
        m = re.search(r"(?:shortest|lowest)\s+(\d+)", q_clean)
        k = 1
        if m:
            k = int(m.group(1))
        return {"attribute": "height", "operator": "BOTTOM", "value": k}

    # Cheapest / least expensive
    if "cheapest" in q_lower or "least expensive" in q_lower or "lowest value" in q_lower:
        m = re.search(r"(?:cheapest|least expensive)\s+(\d+)", q_clean)
        k = 1
        if m:
            k = int(m.group(1))
        return {"attribute": "value", "operator": "BOTTOM", "value": k}

    # Most expensive / highest value
    if "most expensive" in q_lower or "highest value" in q_lower or "priciest" in q_lower:
        m = re.search(r"(?:most expensive|priciest)\s+(\d+)", q_clean)
        k = 1
        if m:
            k = int(m.group(1))
        return {"attribute": "value", "operator": "TOP", "value": k}

    # --- Zoning / type intents ---
    if "residential" in q_lower:
        return {"attribute": "type", "operator": "=", "value": "residential"}

    if "commercial" in q_lower or "office" in q_lower or "retail" in q_lower:
        return {"attribute": "type", "operator": "=", "value": "commercial"}

    if "mixed use" in q_lower or "mixed-use" in q_lower or "mixed" in q_lower:
        return {"attribute": "type", "operator": "=", "value": "mixed"}

    # Direct zoning code like RC-G, C-COR, MU-1 etc.
    code_match = re.search(r"\b([a-z]{1,3}-[a-z0-9]+)\b", q_clean)
    if code_match:
        code = code_match.group(1).upper()
        return {"attribute": "zoning", "operator": "=", "value": code}

    # --- Range queries: "between X and Y" ---
    between_match = re.search(
        r"between\s+(\d+(?:\.\d+)?)\s+and\s+(\d+(?:\.\d+)?)", q_clean
    )
    if between_match:
        low = _to_float(between_match.group(1))
        high = _to_float(between_match.group(2))
        if low is not None and high is not None and low <= high:
            attr = _guess_attribute(q_lower, q_raw)
            if attr == "height":
                low = _convert_units(q_lower, low)
                high = _convert_units(q_lower, high)
            return {
                "attribute": attr,
                "operator": "BETWEEN",
                "value": [low, high],
            }

    # --- "over / greater than / above" ---
    over_match = re.search(
        r"(over|greater than|more than|above)\s+(\d+(?:\.\d+)?)", q_clean
    )
    if over_match:
        num = _to_float(over_match.group(2))
        if num is not None:
            attr = _guess_attribute(q_lower, q_raw)
            if attr == "height":
                num = _convert_units(q_lower, num)
            return {"attribute": attr, "operator": ">", "value": num}

    # --- "under / less than / below" ---
    under_match = re.search(
        r"(under|less than|below|smaller than)\s+(\d+(?:\.\d+)?)", q_clean
    )
    if under_match:
        num = _to_float(under_match.group(2))
        if num is not None:
            attr = _guess_attribute(q_lower, q_raw)
            if attr == "height":
                num = _convert_units(q_lower, num)
            return {"attribute": attr, "operator": "<", "value": num}

    # --- Simple "X zoning / zone X" ---
    if "zoning" in q_lower or "zone" in q_lower:
        tokens = q_clean.split()
        if tokens:
            candidate = tokens[-1].upper()
            if re.match(r"^[A-Z]{1,3}-[A-Z0-9]+$", candidate):
                return {
                    "attribute": "zoning",
                    "operator": "=",
                    "value": candidate,
                }

    # --- Bare numeric with no explicit operator (assume "> number") ---
    nums = re.findall(r"(\d+(?:\.\d+)?)", q_clean)
    if nums:
        num = _to_float(nums[0])
        if num is not None:
            attr = _guess_attribute(q_lower, q_raw)
            if attr == "height":
                num = _convert_units(q_lower, num)
            return {"attribute": attr, "operator": ">", "value": num}

    # --- Fallback: simple keywords without numbers ---
    if "tall" in q_lower:
        return {"attribute": "height", "operator": ">", "value": 30.0}
    if "short" in q_lower:
        return {"attribute": "height", "operator": "<", "value": 15.0}
    if "expensive" in q_lower:
        return {"attribute": "value", "operator": ">", "value": 800000.0}
    if "cheap" in q_lower or "inexpensive" in q_lower:
        return {"attribute": "value", "operator": "<", "value": 400000.0}

    # If we get here, we couldn't confidently interpret the query.
    return None


# --------------------------------------------------------------------
# HUGGING FACE CALL
# --------------------------------------------------------------------
def _call_hf_llm(query: str):
    """
    Try to use a Hugging Face text generation model to produce
    a filter JSON. Returns a dict or None on any failure.
    """
    if not HF_API_KEY:
        return None

    prompt = f"""
You are a backend for a 3D city dashboard. Convert the user's query
into a JSON filter with this exact schema:

{{
  "attribute": "height" | "value" | "zoning" | "type",
  "operator": ">" | "<" | "=" | "BETWEEN" | "TOP" | "BOTTOM",
  "value": number | string | [number, number]
}}

Examples:
- "highlight the tallest building" ->
  {{"attribute": "height", "operator": "TOP", "value": 1}}
- "highlight the tallest 3 buildings" ->
  {{"attribute": "height", "operator": "TOP", "value": 3}}
- "highlight buildings over $1,000,000" ->
  {{"attribute": "value", "operator": ">", "value": 1000000}}

Respond with JSON only, no explanation.

User query: "{query}"
"""

    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(
            HF_API_URL,
            headers=headers,
            json={"inputs": prompt},
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()

        # text-generation models typically return a list with "generated_text"
        if isinstance(data, list) and data and "generated_text" in data[0]:
            text = data[0]["generated_text"]
        else:
            text = str(data)

        # Extract first {...} block from the text
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None

        json_str = text[start : end + 1]
        filt = json.loads(json_str)

        # basic sanity check
        if not isinstance(filt, dict):
            return None
        if "attribute" not in filt or "operator" not in filt:
            return None

        return filt
    except Exception as e:
        print("[HF_LLM] Error calling Hugging Face:", repr(e))
        return None


# --------------------------------------------------------------------
# Public entry point used by Flask
# --------------------------------------------------------------------
def interpret_query(query: str):
    """
    Main entry point used by Flask.

    1) Try Hugging Face Inference API (if configured).
    2) Fall back to the rule-based interpreter if HF is not available
       or returns an invalid result.
    """
    hf_filter = _call_hf_llm(query)
    if hf_filter:
        print("[HF_LLM] Using Hugging Face filter:", hf_filter)
        return hf_filter

    # Fallback to your original deterministic logic
    rb_filter = _interpret_rule_based(query)
    print("[RULE_BASED] Using rule-based filter:", rb_filter)
    return rb_filter
