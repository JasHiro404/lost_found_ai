# services/vector_store.py

import faiss
import numpy as np
import os
import json

dimension = 384

INDEX_PATH = "data/faiss_index/index.bin"
MAP_PATH = "data/faiss_index/id_map.json"

# Create folder if not exists
os.makedirs("data/faiss_index", exist_ok=True)

# Load existing index or create new
if os.path.exists(INDEX_PATH):
    index = faiss.read_index(INDEX_PATH)
    print("✅ FAISS index loaded from disk")
else:
    index = faiss.IndexFlatL2(dimension)
    print("🆕 New FAISS index created")

# Load existing id_map or start fresh
if os.path.exists(MAP_PATH):
    with open(MAP_PATH, "r") as f:
        id_map = json.load(f)
    print(f"✅ ID map loaded: {len(id_map)} entries")
else:
    id_map = []


def save_to_disk():
    faiss.write_index(index, INDEX_PATH)
    with open(MAP_PATH, "w") as f:
        json.dump(id_map, f)


def add_vector(vector, item_id):
    vector = np.array([vector]).astype('float32')
    index.add(vector)
    id_map.append(item_id)
    save_to_disk()  # persist immediately


def search_vector(query_vector, k=5):
    if index.ntotal == 0:
        return []

    query_vector = np.array([query_vector]).astype('float32')
    actual_k = min(k, index.ntotal)
    distances, indices = index.search(query_vector, actual_k)

    results = []
    seen = set()

    for dist, idx in zip(distances[0], indices[0]):
        if idx != -1 and idx < len(id_map):
            item_id = id_map[idx]
            if item_id not in seen:
                seen.add(item_id)
                similarity = 1 / (1 + dist)
                results.append({
                    "item_id": item_id,
                    "similarity": float(similarity)
                })

    return results