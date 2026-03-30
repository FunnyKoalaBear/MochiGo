import os
from memory.vector_course import KnowledgeBase

def main():
    print("=== RAG Vector Database Tester ===")
    print("Loading Knowledge Base...")
    
    # Initialize the database
    kb = KnowledgeBase()

    # Check if there is actually anything in the database
    chunk_count = kb.course_db._collection.count()
    if chunk_count == 0:
        print("ERROR: Your textbook database is empty! Please run ingest.py first with some PDFs.")
        return

    print(f"Success! Loaded {chunk_count} chunks of text.")
    print("Type a topic or question to see what the database retrieves.")
    print("Type 'quit' to exit.\n")

    while True:
        query = input("Search Query: ")
        if query.lower() in ['quit', 'exit']:
            break

        print("\n--- Searching... ---")
        
        # We use 'similarity_search_with_score' here instead of the standard search.
        # This exposes the underlying math! 
        results = kb.course_db.similarity_search_with_score(query, k=3)

        if not results:
            print("No results found.")
            continue

        for i, (doc, score) in enumerate(results):
            # Extract metadata
            source_path = doc.metadata.get('source', 'Unknown Book')
            filename = os.path.basename(source_path)
            page_num = doc.metadata.get('page', -1) + 1 
            
            # Print the math and the result
            # NOTE: ChromaDB uses "Distance" for its score. 
            # A LOWER number means a BETTER, closer match! (0.0 is a perfect identical match)
            print(f"\n[Result #{i+1} | Distance Score: {score:.4f}]")
            print(f"Source: {filename} (Page {page_num})")
            
            # We print the first 400 characters so it doesn't flood your terminal, 
            # but gives you enough to verify relevance.
            preview = doc.page_content[:400].replace('\n', ' ')
            print(f"Excerpt: {preview}...")

        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()