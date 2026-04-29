# services/embedding.py

from sentence_transformers import SentenceTransformer

# Load model once (important)
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text):
    """
    Converts text → vector (list of numbers)
    """
    embedding = model.encode(text)
    return embedding