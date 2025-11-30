"""
SKILL MASTERED: RAG (Retrieval Augmented Generation) with Vector DB
Week 1 Day 3

What I learned:
- ChromaDB vector database setup
- Document embedding and semantic search
- Context retrieval for LLM prompts
- Building personal knowledge systems

Portfolio highlight:
"Built RAG-powered AI coach that retrieves relevant context from personal knowledge base before generating responses"

Business value:
- Privacy-first (all data local)
- Scalable (add documents anytime)
- Personalized (remembers user-specific info)
"""

import chromadb


def demo():
    """Quick demo of RAG skill"""
    client = chromadb.Client()
    collection = client.create_collection("demo")

    collection.add(
        documents=["I know econometrics and time series analysis"], ids=["skill1"]
    )

    results = collection.query(query_texts=["statistical methods"], n_results=1)
    print(f"Found: {results['documents'][0][0]}")


if __name__ == "__main__":
    demo()
