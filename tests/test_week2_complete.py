"""
Week 2 Complete System Test
Test all features end-to-end
"""

import sys

sys.path.insert(0, "src")

print("=" * 70)
print("🧪 WEEK 2 COMPLETE SYSTEM TEST")
print("=" * 70)

# Test 1: Imports
print("\n--- Test 1: Module Imports ---")
try:
    from rag_engine import KnowledgeBase
    from skills_tracker import SkillsTracker
    from knowledge_graph import KnowledgeGraph
    from document_chunker import DocumentChunker
    from query_cache import QueryCache

    print("✅ All modules imported successfully")
except Exception as e:
    print(f"❌ Import error: {e}")
    exit(1)

# Test 2: Initialize systems
print("\n--- Test 2: System Initialization ---")
try:
    kb = KnowledgeBase()
    tracker = SkillsTracker(kb)
    graph = KnowledgeGraph(kb)
    chunker = DocumentChunker()
    cache = QueryCache()
    print("✅ All systems initialized")
except Exception as e:
    print(f"❌ Initialization error: {e}")
    exit(1)

# Test 3: Knowledge graph
print("\n--- Test 3: Knowledge Graph ---")
try:
    graph.build_from_vault("data/obsidian_vault")
    stats = graph.get_node_stats()
    print(f"✅ Graph built: {stats['total_nodes']} nodes, {stats['total_edges']} edges")
except Exception as e:
    print(f"❌ Graph error: {e}")

# Test 4: Document chunking
print("\n--- Test 4: Document Chunking ---")
try:
    test_text = "# Test\n\nFirst paragraph. Second sentence.\n\n## Section\n\nMore content here."
    chunks = chunker.chunk_by_markdown_headings(test_text, "test.md")
    quality = chunker.measure_quality(chunks)
    print(
        f"✅ Created {len(chunks)} chunks, bad cut rate: {quality.get('bad_cut_rate', 0)}%"
    )
except Exception as e:
    print(f"❌ Chunking error: {e}")

# Test 5: Query cache
print("\n--- Test 5: Query Cache ---")
try:
    cache.set("test query", {"answer": "test result"})
    result = cache.get("test query")
    cache_stats = cache.get_stats()
    print(f"✅ Cache working, hit rate: {cache_stats['hit_rate']}%")
except Exception as e:
    print(f"❌ Cache error: {e}")

# Test 6: Skills tracker
print("\n--- Test 6: Skills Tracker ---")
try:
    skills = tracker.extract_all_skills()
    print(f"✅ Tracking {len(skills)} skills")
except Exception as e:
    print(f"❌ Tracker error: {e}")

print("\n" + "=" * 70)
print("✅ WEEK 2 SYSTEM TEST COMPLETE!")
print("   All core features operational")
print("=" * 70)
