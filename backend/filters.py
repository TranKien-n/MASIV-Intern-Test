def apply_filter(buildings, filt):
    """Return list of building IDs that match the filter."""
    attr = filt.get("attribute")
    op = filt.get("operator")
    raw_value = filt.get("value")

    try:
        value = float(raw_value)
    except:
        return []

    def matches(b):
        if attr not in b:
            return False
        try:
            bv = float(b[attr])
        except:
            return False

        if op == ">":
            return bv > value
        elif op == "<":
            return bv < value
        elif op == "=":
            return bv == value
        return False

    return [b["id"] for b in buildings if matches(b)]
