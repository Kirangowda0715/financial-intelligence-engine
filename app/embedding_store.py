import chromadb
from sentence_transformers import SentenceTransformer
import uuid

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# ChromaDB 1.x requires PersistentClient, not Client+Settings
chroma_client = chromadb.PersistentClient(path="chroma_storage")

collection = chroma_client.get_or_create_collection(
    name="financial_documents"
)


def generate_embedding(text: str):
    return embedding_model.encode(text).tolist()


def store_chunks(chunks, company_name="Unknown", quarter="Unknown"):
    document_id = str(uuid.uuid4())

    ids = []
    documents = []
    embeddings = []
    metadatas = []

    for chunk in chunks:
        chunk_unique_id = f"{document_id}_{chunk['chunk_id']}"

        ids.append(chunk_unique_id)
        documents.append(chunk["text"])
        embeddings.append(generate_embedding(chunk["text"]))

        metadatas.append({
            "document_id": document_id,
            "company": company_name,
            "quarter": quarter,
            "speaker_name": chunk.get("speaker_name", "Unknown"),
            "speaker_role": chunk.get("speaker_role", "Unknown"),
            "section_type": chunk.get("section_type", "Unknown")
        })

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return document_id