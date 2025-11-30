"""
RAG (Retrieval Augmented Generation) Engine
Week 1 Day 3 - Your personal knowledge base brain
"""

import os
import chromadb


class KnowledgeBase:
    def __init__(self, kb_path="data/knowledge_base"):
        self.kb_path = kb_path

        # Initialize ChromaDB (NEW API)
        self.client = chromadb.PersistentClient(path="data/vector_db")

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="career_knowledge",
            metadata={"description": "Economist skills and transition goals"},
        )

        print(f"📚 Knowledge Base initialized")
        print(f"   Stored documents: {self.collection.count()}")

    def load_knowledge_files(self):
        """Load all text files from knowledge base folder"""
        skills_folder = os.path.join(self.kb_path, "skills")

        if not os.path.exists(skills_folder):
            print(f"⚠️ Create folder first: {skills_folder}")
            return

        files_loaded = 0
        for filename in os.listdir(skills_folder):
            if filename.endswith(".txt"):
                filepath = os.path.join(skills_folder, filename)

                # Read file content
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                # Add to vector database
                doc_id = filename.replace(".txt", "")
                self.collection.upsert(
                    documents=[content],
                    ids=[doc_id],
                    metadatas=[{"source": filename, "type": "skill_inventory"}],
                )

                files_loaded += 1
                print(f"   ✓ Loaded: {filename}")

        print(f"\n✅ Loaded {files_loaded} knowledge files into vector DB")

    def search(self, query, n_results=2):
        """Search knowledge base for relevant information"""
        results = self.collection.query(query_texts=[query], n_results=n_results)

        if not results["documents"][0]:
            return "No relevant knowledge found."

        # Format results
        context = "\n\n".join(results["documents"][0])
        return context

    def get_stats(self):
        """Show knowledge base statistics"""
        count = self.collection.count()
        print(f"\n📊 Knowledge Base Stats:")
        print(f"   Total documents: {count}")
        if count > 0:
            # Sample a document
            sample = self.collection.peek(limit=1)
            print(f"   Sample document: {sample['ids'][0]}")


# Quick test
if __name__ == "__main__":
    kb = KnowledgeBase()

    print("\n--- Loading Knowledge Files ---")
    kb.load_knowledge_files()

    print("\n--- Testing Search ---")
    query = "What econometric skills do I have?"
    print(f"Query: {query}\n")
    context = kb.search(query)
    print(f"Found context:\n{context[:300]}...")

    kb.get_stats()
