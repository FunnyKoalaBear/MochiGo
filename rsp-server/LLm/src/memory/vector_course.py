import os
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

DB_DIR = "rsp-server/LLm/data/chroma_knowledge"
PDF_DIR = "rsp-server/LLm/data/course_materials"
DICT_DIR = "rsp-server/LLm/data/dictionary_materials" # NEW
EMBEDDING_MODEL = "nomic-embed-text"

class KnowledgeBase:
    def __init__(self):
        os.makedirs(DB_DIR, exist_ok=True)
        os.makedirs(PDF_DIR, exist_ok=True)
        os.makedirs(DICT_DIR, exist_ok=True) # NEW
        
        self.embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
        
        self.course_db = Chroma(collection_name="coursebook", embedding_function=self.embeddings, persist_directory=DB_DIR)
        self.dict_db = Chroma(collection_name="dictionary", embedding_function=self.embeddings, persist_directory=DB_DIR)

    def _process_pdfs(self, directory, database, chunk_size, chunk_overlap):
        """Helper function to process PDFs for either DB in safe batches."""
        pdf_files = [f for f in os.listdir(directory) if f.endswith('.pdf')]
        if not pdf_files:
            print(f"DEBUG: No PDFs found in {directory}.")
            return

        print(f"DEBUG: Found {len(pdf_files)} PDFs in {directory}. Starting ingestion...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len)
        all_chunks = []

        for filename in pdf_files:
            filepath = os.path.join(directory, filename)
            print(f"DEBUG: Reading '{filename}'...")
            loader = PyPDFLoader(filepath)
            pages = loader.load()
            for page in pages:
                page.page_content = page.page_content.replace('\n', ' ').replace('  ', ' ').strip()
            chunks = text_splitter.split_documents(pages)
            all_chunks.extend(chunks)

        if all_chunks:
            # NEW: Batch insertion to prevent ChromaDB from crashing on massive files
            batch_size = 5000
            total_chunks = len(all_chunks)
            print(f"DEBUG: Preparing to insert {total_chunks} chunks in batches of {batch_size}...")
            
            for i in range(0, total_chunks, batch_size):
                batch = all_chunks[i : i + batch_size]
                database.add_documents(batch)
                print(f"DEBUG: -> Inserted chunks {i} to {i + len(batch)}")
                
            print(f"DEBUG: Successfully ingested all {total_chunks} chunks!")

    def ingest_pdfs(self):
        # Textbooks get larger chunks for wider context
        self._process_pdfs(PDF_DIR, self.course_db, chunk_size=1000, chunk_overlap=200)

    def ingest_dictionaries(self):
        # Dictionaries get smaller chunks because definitions are short and dense
        self._process_pdfs(DICT_DIR, self.dict_db, chunk_size=400, chunk_overlap=50)

    def retrieve_course_topic(self, query: str, k=2) -> str:
        if self.course_db._collection.count() == 0: return "No textbook data available."
        results = self.course_db.similarity_search(query, k=k)
        return self._format_results(results)

    def retrieve_dictionary_word(self, word: str, k=3) -> str:
        if self.dict_db._collection.count() == 0: return "No dictionary data available."
        # We fetch 3 chunks for dictionaries to ensure we catch the exact word definition
        results = self.dict_db.similarity_search(word, k=k)
        return self._format_results(results)

    def _format_results(self, results) -> str:
        reference_material = ""
        for i, res in enumerate(results):
            filename = os.path.basename(res.metadata.get('source', 'Unknown'))
            page_num = res.metadata.get('page', -1) + 1 
            reference_material += f"--- SOURCE: {filename} (Page {page_num}) ---\n{res.page_content}\n\n"
        return reference_material