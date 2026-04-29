from services.embedding import get_embedding
from services.vector_store import add_vector, search_vector

# sample data
items = [
    ("Black wallet lost near library", 1),
    ("Blue bottle found in classroom", 2),
    ("Phone lost near canteen", 3),
]

# add vectors
for text, item_id in items:
    vec = get_embedding(text)
    add_vector(vec, item_id)

# search
query = "lost wallet near VIT library"
query_vec = get_embedding(query)

results = search_vector(query_vec)

for r in results:
    print(r)