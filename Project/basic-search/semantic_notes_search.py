from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

NOTES_DIR = Path("notes")
COLLECTION_NAME = "notes_embeddings"
EMBED_MODEL = "all-MiniLM-L6-v2"
QDRANT_URL = "http://localhost:6333"

model = SentenceTransformer(EMBED_MODEL)
client = QdrantClient(url=QDRANT_URL)

client.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(
        size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE
    ),
)


def load_notes(directory: Path):
    notes = []
    for file in directory.glob("**/*"):
        if file.suffix.lower() in [".md", ".txt"]:
            content = file.read_text(encoding="utf-8", errors="ignore")
            if content.strip():
                notes.append((file.name, content))
    return notes


notes = load_notes(NOTES_DIR)
print(f"Loaded {len(notes)} notes.")

points = []
for i, (fname, content) in enumerate(tqdm(notes, desc="Embedding notes")):
    vector = model.encode(content).tolist()
    payload = {"filename": fname, "content": content[:1000]}  # truncate long payloads
    points.append(PointStruct(id=i, vector=vector, payload=payload))

client.upsert(collection_name=COLLECTION_NAME, points=points)
print(f"Inserted {len(points)} notes into Qdrant!")


def semantic_search(query: str, top_k: int = 3):
    q_emb = model.encode(query).tolist()
    results = client.search(
        collection_name=COLLECTION_NAME, query_vector=q_emb, limit=top_k
    )
    for i, r in enumerate(results, 1):
        print(f"\n[{i}] {r.payload['filename']} (score={r.score:.4f})")
        print(r.payload["content"][:300], "...\n")


while True:
    query = input("\nSearch > ").strip()
    if query.lower() in {"exit", "quit"}:
        break
    semantic_search(query)
