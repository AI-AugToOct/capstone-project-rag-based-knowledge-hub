from backend.document_loader import load_documents_from_store, split_documents
from backend.embedding_generator import EmbeddingGenerator
from backend.config import DOCUMENT_STORE_PATH
from backend.report_generator import generate_report 

class RAGWorkflow:
    def __init__(self):
        self.embedding_generator = EmbeddingGenerator()

    def setup_knowledge_base(self):
        # Load and split documents
        documents = load_documents_from_store(DOCUMENT_STORE_PATH)
        if not documents:
            print("⚠️ No documents found in store. Knowledge base is empty.")
            return

        chunks = [doc["content"] for doc in split_documents(documents)]
        
        # Create vector store
        self.embedding_generator.create_vector_store(chunks)
        print("✅ Knowledge base setup complete!")

    def answer_query(self, query, k=5):
        # Search similar chunks (returns list of {chunk, distance})
        results = self.embedding_generator.search_similar_chunks(query, k=k)
        if not results:
            return "No relevant information found in knowledge base."

        # Concatenate top-k chunks as context
        context = "\n".join([r["chunk"] for r in results])

        # Generate context-aware answer using Gemini (inside generate_report)
        answer = generate_report(context, query)
        return answer
