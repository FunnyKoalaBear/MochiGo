import os
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

# Configuration
DB_DIR = "rsp-server/LLm/data/chroma_history"
EMBEDDING_MODEL = "nomic-embed-text"

class VectorMemory:
    def __init__(self):
        os.makedirs(DB_DIR, exist_ok=True)
        # Initialize the embedding function
        self.embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
        
        # Connect to the Chroma database
        self.db = Chroma(
            collection_name="mochigo_history",
            embedding_function=self.embeddings,
            persist_directory=DB_DIR
        )

    def save_memory(self, role: str, content: str):
        """Embeds and saves a single interaction to the vector database."""
        # We format it nicely so the DB knows who said what
        text_to_save = f"[{role.upper()}]: {content}"
        
        # Add to ChromaDB
        self.db.add_texts(texts=[text_to_save], metadatas=[{"role": role}])
        #print(f"DEBUG: Saved to Vector DB -> {text_to_save[:30]}...\n\n")

    def retrieve_relevant_memories(self, current_input: str, k=3) -> str:
        """Searches for the top 'k' most relevant past memories based on the current context."""
        # If the database is empty, return nothing
        if self.db._collection.count() == 0:
            return ""

        # Perform similarity search
        results = self.db.similarity_search(current_input, k=k)
        
        if not results:
            return ""

        memory_str = "Relevant Past Memories:\n"
        for res in results:
            memory_str += f"- {res.page_content}\n"
        
        #print(f"DEBUG: Retrieved from Vector DB -> {memory_str}...\n\n")
        return memory_str