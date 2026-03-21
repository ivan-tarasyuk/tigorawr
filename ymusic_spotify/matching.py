def match_str(str_1: str, str_2: str, *, a: int, b: int, c: int) -> int:
    """Compare two strings and return weighted score

    Scoring:
        a - exact match
        b - prefix match (one starts with another)
        c - one or both strings are empty
        0 - no match
    """
    if not str_1 or not str_2:
        return c
    if str_1 == str_2:
        return a
    if str_1.startswith(str_2) or str_2.startswith(str_1):
        return b
    return 0


def match_set(set_1: set, set_2: set, *, a: int, b: int) -> int:
    """Compare two sets and return weighted score

    Scoring:
        a - exact match
        b - subset/superset relationship
        0 - no meaningful overlap
    """
    if set_1 == set_2:
        return a
    if set_1 > set_2 or set_1 < set_2:
        return b
    return 0
