from langchain_huggingface import HuggingFaceEmbeddings
import pickle
import os
import sys

# Path settings
CHUNKS_PATH = "app/chunks.pkl"
EMBEDDINGS_DIR = "app/embeddings"
EMBEDDINGS_PATH = os.path.join(EMBEDDINGS_DIR, "embeddings.pkl")

# Define embedding model
print("🔍 Loading HuggingFace embedding model...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Validate pickle file
if not os.path.exists(CHUNKS_PATH):
    print(f"❌ ERROR: Chunks file not found at {CHUNKS_PATH}. Run preprocessing.py first.")
    sys.exit(1)

if os.path.getsize(CHUNKS_PATH) == 0:
    print(f"❌ ERROR: Chunks file is empty. Check preprocessing.py output.")
    sys.exit(1)

# Load preprocessed chunks
print("📂 Loading chunks...")
with open(CHUNKS_PATH, "rb") as f:
    try:
        chunks = pickle.load(f)
    except EOFError:
        print("❌ ERROR: Failed to load chunks. File may be corrupted.")
        sys.exit(1)

# Prepare documents & metadata
docs = [chunk.page_content for chunk in chunks]
metadatas = [chunk.metadata for chunk in chunks]
print(f"📊 Total chunks to embed: {len(docs)}")

if not docs:
    print("❌ ERROR: No documents found in chunks. Check preprocessing step.")
    sys.exit(1)

# Generate embeddings
print("⚡ Generating embeddings...")
doc_embeddings = embeddings.embed_documents(docs)
print(f"✅ Generated embeddings with dimension: {len(doc_embeddings[0])}")

# Save embeddings
embedding_data = {
    "docs": docs,
    "metadatas": metadatas,
    "embeddings": doc_embeddings
}

os.makedirs(EMBEDDINGS_DIR, exist_ok=True)
with open(EMBEDDINGS_PATH, "wb") as f:
    pickle.dump(embedding_data, f)

print(f"🎉 Embeddings generated and saved successfully at {EMBEDDINGS_PATH}")
