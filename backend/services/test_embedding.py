from services.embedding import get_embedding

text = "Black wallet lost near VIT Pune library"

vector = get_embedding(text)

print("Vector length:", len(vector))
print("First 5 values:", vector[:5])