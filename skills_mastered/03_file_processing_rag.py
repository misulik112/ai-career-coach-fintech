"""
SKILL MASTERED: File Processing + RAG Integration
Week 1 Day 4

What I learned:
- Reading text and PDF files programmatically
- Extracting content from multiple file formats
- Integrating document loading with vector database
- Building job requirement analyzers

Portfolio highlight:
"Built intelligent job analyzer - upload job description, get instant skills gap analysis using RAG + LLM"

Business value:
- Automates career research (saves hours per job application)
- Data-driven skill development (focus on high-ROI learning)
- Scalable (add unlimited job posts, auto-indexed)
"""

from src.file_processor import FileProcessor
from src.rag_engine import KnowledgeBase


def demo():
    """Demo job analysis workflow"""
    processor = FileProcessor()
    kb = KnowledgeBase()

    # Load job
    job = processor.load_file(
        "data/monitored_folders/job_posts/python_finance_analyst.txt"
    )
    print(f"Loaded: {job['filename']} - {job['word_count']} words")

    # Search for requirements
    results = kb.search("Python skills required")
    print(f"Found requirements: {results[:100]}...")


if __name__ == "__main__":
    demo()
