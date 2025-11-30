"""
Test Suite for AI Career Coach
Week 1 Day 6 - Verify all components work
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from llm_engine import LocalLLM
from rag_engine import KnowledgeBase
from file_processor import FileProcessor
from main import CareerCoach


def test_llm():
    """Test local LLM connection"""
    print("\n🧪 Testing Local LLM...")
    llm = LocalLLM()
    response = llm.chat("Say 'test passed' in one word")
    assert len(response) > 0, "LLM response empty!"
    print(f"   ✅ LLM working: {response[:50]}...")


def test_knowledge_base():
    """Test vector database"""
    print("\n🧪 Testing Knowledge Base...")
    kb = KnowledgeBase()

    # Load skills
    kb.load_knowledge_files()
    count = kb.collection.count()
    assert count > 0, "No documents loaded!"
    print(f"   ✅ Vector DB has {count} documents")

    # Test search
    results = kb.search("econometrics")
    assert len(results) > 0, "Search returned nothing!"
    print(f"   ✅ Search working: {len(results)} chars returned")


def test_file_processor():
    """Test file loading"""
    print("\n🧪 Testing File Processor...")
    processor = FileProcessor()

    # Load job posts folder
    files = processor.load_folder("data/monitored_folders/job_posts")
    assert len(files) > 0, "No files loaded!"
    print(f"   ✅ Loaded {len(files)} file(s)")


def test_coach():
    """Test full coach integration"""
    print("\n🧪 Testing Full Coach...")
    coach = CareerCoach(enable_watcher=False)
    coach.load_knowledge()

    response = coach.chat("What are my top economist skills?")
    assert len(response) > 0, "Coach didn't respond!"
    print(f"   ✅ Coach responding: {response[:80]}...")


def run_all_tests():
    """Run all tests"""
    print("=" * 70)
    print("🧪 AI CAREER COACH - TEST SUITE")
    print("=" * 70)

    try:
        test_llm()
        test_knowledge_base()
        test_file_processor()
        test_coach()

        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        return True

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n⚠️ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
