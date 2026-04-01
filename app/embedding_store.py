import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import uuid

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

chroma_client = chromadb.Client(
    Settings(persist_directory="chroma_storage")
)

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
            "speaker_name": chunk["speaker_name"],
            "speaker_role": chunk["speaker_role"],
            "section_type": chunk["section_type"]
        })

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return document_id