import chromadb
from sentence_transformers import SentenceTransformer
from datetime import datetime
import os

# Load a lightweight local embedding model (no API key needed)
# This runs entirely on your machine
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# This creates a local folder called "chroma_db" in your project root
# All your research memory gets saved here permanently on disk
client = chromadb.PersistentClient(path="./chroma_db")

# A "collection" is like a table in a database — this is where all research is stored
collection = client.get_or_create_collection(name="research_memory")


def save_research(topic: str, content: str):
    """
    Saves a research result to memory.
    topic  — the search query or subject (e.g. "Nvidia vs AMD deep learning")
    content — the raw text content to remember
    """
    embedding = embedding_model.encode(content).tolist()

    # Each entry needs a unique ID — we use topic + timestamp
    unique_id = f"{topic[:50]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    collection.add(
        ids=[unique_id],
        embeddings=[embedding],
        documents=[content],
        metadatas=[{"topic": topic, "timestamp": datetime.now().isoformat()}]
    )

    print(f"[Memory] Saved research for topic: '{topic}'")


def retrieve_similar_research(query: str, n_results: int = 3) -> list:
    """
    Searches memory for past research similar to the current query.
    Returns a list of previously saved content chunks.
    """
    query_embedding = embedding_model.encode(query).tolist()

    # Check how many items exist before querying
    total = collection.count()
    if total == 0:
        print("[Memory] No past research found in memory.")
        return []

    # Don't ask for more results than what exists
    n_results = min(n_results, total)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    print(f"[Memory] Found {len(documents)} similar past research entries.")
    return [{"content": doc, "metadata": meta} for doc, meta in zip(documents, metadatas)]


def clear_memory():
    """
    Wipes all stored research. Useful during development/testing.
    """
    global collection
    client.delete_collection(name="research_memory")
    collection = client.get_or_create_collection(name="research_memory")
    print("[Memory] All research memory cleared.")