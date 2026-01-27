from main import MyCustomVectorStore # Import your renamed class
import pprint

def run_health_check():
    print("--- 🔍 Starting Vector Search Health Check ---")
    
    # 1. Initialize the Store
    # Reminder: Ensure index_name="default" inside this class 
    # since that's what the Atlas CLI showed.
    store = MyCustomVectorStore()
    
    # 2. Define your test query
    query = "I have GST notice how to reply"
    
    print(f"Testing query: '{query}'...")
    
    # 3. Perform Similarity Search
    try:
        # k=3 returns the top 3 most relevant chunks
        results = store.vector_store.similarity_search(query, k=3)
        
        if not results:
            print("❌ No results found. Possible reasons:")
            print("  - The Vector Index is still building (check Atlas CLI status).")
            print("  - No documents have been uploaded to 'knowledge_base' yet.")
            print("  - The 'numDimensions' in the index doesn't match the model (768).")
        else:
            print(f"✅ Success! Found {len(results)} matching chunks:\n")
            for i, doc in enumerate(results):
                print(f"Result #{i+1} (Page {doc.metadata.get('page_num', 'N/A')}):")
                print(f"Text snippet: {doc.page_content[:200]}...")
                print("-" * 30)
                
    except Exception as e:
        print(f"💥 Search Error: {str(e)}")

if __name__ == "__main__":
    run_health_check()