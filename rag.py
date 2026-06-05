import os
try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = ' '.join(words[i:i+chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks

def process_pdf_with_rag(pdf_text, query, top_k=3):
    if not CHROMA_AVAILABLE:
        return pdf_text[:2000]
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        chunks = chunk_text(pdf_text)
        if not chunks:
            return pdf_text[:2000]
        client = chromadb.Client(Settings(anonymized_telemetry=False))
        collection_name = "pdf_chunks"
        try:
            client.delete_collection(collection_name)
        except:
            pass
        collection = client.create_collection(collection_name)
        embeddings = model.encode(chunks).tolist()
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        collection.add(embeddings=embeddings, documents=chunks, ids=ids)
        query_embedding = model.encode([query]).tolist()
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=min(top_k, len(chunks))
        )
        relevant_chunks = results['documents'][0]
        return '\n\n'.join(relevant_chunks)
    except Exception as e:
        print(f"RAG failed, falling back to truncation: {e}")
        return pdf_text[:2000]