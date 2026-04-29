# services/matcher.py

from services.embedding import get_embedding
from services.vector_store import search_vector

SIMILARITY_THRESHOLD = 0.4  # tune this later

def find_matches(new_item, all_items_opposite_type):
    """
    Given a new item, find similar items of opposite type.
    new_item: dict with title, description, location, id
    all_items_opposite_type: list of dicts from MySQL
    """
    text = f"{new_item['title']} {new_item['description']} {new_item['location']}"
    query_vector = get_embedding(text)

    results = search_vector(query_vector)

    # Filter to only return opposite-type matches above threshold
    matches = []
    for r in results:
        if r['similarity'] >= SIMILARITY_THRESHOLD:
            matches.append(r)

    return matches