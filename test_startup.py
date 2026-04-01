import time
print("Starting...")

print("Importing chromadb...")
import chromadb
from chromadb.config import Settings
print("Init chroma client...")
chroma_client = chromadb.Client(Settings(persist_directory="chroma_storage"))
print("Init chroma collection...")
collection = chroma_client.get_or_create_collection(name="financial_documents")
print("ChromaDB done.")

print("Importing SentenceTransformer...")
from sentence_transformers import SentenceTransformer
print("Init embedding model...")
start = time.time()
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
print(f"SentenceTransformer done in {time.time()-start:.2f}s.")

print("All done.")
