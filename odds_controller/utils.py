import re


def is_matching_query(o1: str, o2: str, query: str) -> bool:
    for q in re.split('[- ]', query.lower()):
        for o in re.split('[- ]', o1.lower()) + (re.split('[- ]', o2.lower())):
            if o.startswith(q):
                return True
    return False
