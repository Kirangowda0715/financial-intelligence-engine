from app.embedding_store import collection, generate_embedding


def retrieve_chunks(query, top_k=8, company=None, quarter=None, section_type=None):
    query_embedding = generate_embedding(query)

    filters = {}

    if company:
        filters["company"] = company

    if quarter:
        filters["quarter"] = quarter

    if section_type:
        filters["section_type"] = section_type

    where_clause = filters if filters else None

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_clause,
        include=["documents", "metadatas", "distances"]
    )

    retrieved_docs = []

    if results["documents"]:
        for i in range(len(results["documents"][0])):
            retrieved_docs.append({
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "score": results["distances"][0][i]
            })

    return retrieved_docs

def get_document_chunks(document_id, limit=20):
    results = collection.get(
        where={"document_id": document_id},
        include=["documents", "metadatas"]
    )
    
    chunks = []
    if results["documents"]:
        # ChromaDB get() order is arbitrary, so we sort by chunk_id from metadata if possible
        # However, our current metadata doesn't have chunk_id explicitly. 
        # But we need sequential context. If we can't sort accurately, we at least return the raw texts.
        for doc, meta in zip(results["documents"], results["metadatas"]):
            chunks.append({
                "text": doc,
                "metadata": meta
            })
            
    return chunks[:limit]