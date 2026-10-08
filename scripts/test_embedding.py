import time

from sentence_transformers import SentenceTransformer

MODEL_NAME = "BAAI/bge-m3"

t0 = time.perf_counter()
model = SentenceTransformer(MODEL_NAME, device='cpu')
print(f'Model loaded in {time.perf_counter() - t0:.1f}s')

# show the model pipeline
print(model)

sentences = [
    "il gatto dorme sul divano",
    "un felino riposa sul sofà",
    "fattura n. 4521 del 3 marzo"
]

t0 = time.perf_counter()
embeddings = model.encode(sentences, normalize_embeddings=True)
print(f'Encoded {len(sentences)} sentences in {time.perf_counter() - t0:.2f}s')

print("Shape: ", embeddings.shape)
print("Norms: ", (embeddings**2).sum(axis=1) ** 0.5) # expected to be 1 (normalization works well)

# pairwise similarity matrix 3x3
sims = embeddings @ embeddings.T
for sentence, row in zip(sentences, sims):
    print(f'{sentence:30s}', " ".join(f'{v:.3f}' for v in row))