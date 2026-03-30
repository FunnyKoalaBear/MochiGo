from memory.vector_course import KnowledgeBase

def main():
    print("=== MochiGo Knowledge Ingestion Utility ===")
    kb = KnowledgeBase()
    
    print("\n1. Ingest Coursebooks (Textbooks/Lessons)")
    print("2. Ingest Dictionaries (Vocabulary/Definitions)")
    choice = input("\nSelect an option (1 or 2): ")
    
    if choice == '1':
        kb.ingest_pdfs()
    elif choice == '2':
        kb.ingest_dictionaries()
    else:
        print("Invalid choice. Exiting.")

if __name__ == "__main__":
    main()