"""
RAG Quality Analyzer
Week 3 Day 19 - Test and validate your multi-format knowledge base
"""

from typing import Dict, List, Optional, Tuple
from pathlib import Path
import time
from datetime import datetime


class RAGQualityAnalyzer:
    """Analyze and validate RAG system quality"""

    def __init__(self, knowledge_base):
        self.kb = knowledge_base

        self.test_queries = {
            "skills": [
                "What Python skills do I have?",
                "What are my economist skills?",
                "What programming languages do I know?",
            ],
            "goals": [
                "What is my career transition goal?",
                "How much do I want to earn as a freelancer?",
                "What is my timeline for transition?",
            ],
            "technical": [
                "What Python libraries for finance?",
                "How to use pandas for data analysis?",
                "What is RAG?",
            ],
            "job_market": [
                "What Python skills are required for jobs?",
                "What are typical salaries for Python finance roles?",
                "What companies hire Python developers?",
            ],
        }

        print(f"📊 RAG Quality Analyzer initialized")

    def analyze_collection_stats(self) -> Dict:
        """Analyze knowledge base statistics"""
        print("\n" + "=" * 70)
        print("📊 KNOWLEDGE BASE STATISTICS")
        print("=" * 70)

        # Get all documents
        sample = self.kb.collection.get()

        total_docs = len(sample["ids"])

        # Count by type
        type_counts = {}
        format_counts = {}

        for i, metadata in enumerate(sample["metadatas"]):
            doc_type = metadata.get("type", "unknown")
            source = metadata.get("source", "")

            # Count by type
            type_counts[doc_type] = type_counts.get(doc_type, 0) + 1

            # Count by format
            if "pdf" in doc_type or source.endswith(".pdf"):
                format_counts["PDF"] = format_counts.get("PDF", 0) + 1
            elif "docx" in doc_type or source.endswith(".docx"):
                format_counts["DOCX"] = format_counts.get("DOCX", 0) + 1
            elif "image" in doc_type or "ocr" in doc_type:
                format_counts["Image (OCR)"] = format_counts.get("Image (OCR)", 0) + 1
            elif "anytype" in sample["ids"][i]:
                format_counts["Anytype"] = format_counts.get("Anytype", 0) + 1
            elif source.endswith(".txt"):
                format_counts["TXT"] = format_counts.get("TXT", 0) + 1
            elif source.endswith(".md"):
                format_counts["Markdown"] = format_counts.get("Markdown", 0) + 1
            else:
                format_counts["Other"] = format_counts.get("Other", 0) + 1

        # Calculate total content size
        total_words = sum(len(doc.split()) for doc in sample["documents"])
        avg_words = total_words / total_docs if total_docs > 0 else 0

        stats = {
            "total_documents": total_docs,
            "total_words": total_words,
            "avg_words_per_doc": round(avg_words, 1),
            "type_distribution": type_counts,
            "format_distribution": format_counts,
        }

        # Print results
        print(f"\n📚 Total Documents: {total_docs}")
        print(f"📝 Total Words: {total_words:,}")
        print(f"📊 Average Words/Doc: {avg_words:.1f}")

        print(f"\n📂 By Format:")
        for fmt, count in sorted(
            format_counts.items(), key=lambda x: x[1], reverse=True
        ):
            percentage = (count / total_docs * 100) if total_docs > 0 else 0
            bar = "█" * int(percentage / 5)
            print(f"   {fmt:<20} {count:>3} docs  {bar} {percentage:.1f}%")

        print(f"\n🏷️  By Type:")
        for doc_type, count in sorted(
            type_counts.items(), key=lambda x: x[1], reverse=True
        ):
            print(f"   {doc_type:<25} {count:>3} docs")

        return stats

    def test_retrieval_quality(self, category: str = "all", n_results: int = 3) -> Dict:
        """Test retrieval quality for different query types"""
        print("\n" + "=" * 70)
        print(f"🔍 RETRIEVAL QUALITY TEST - {category.upper()}")
        print("=" * 70)

        # Select queries
        if category == "all":
            queries = []
            for cat_queries in self.test_queries.values():
                queries.extend(cat_queries)
        else:
            queries = self.test_queries.get(category, [])

        if not queries:
            print(f"❌ No test queries for category: {category}")
            return {}

        results = {
            "category": category,
            "queries_tested": len(queries),
            "avg_search_time": 0,
            "successful_retrievals": 0,
            "query_results": [],
        }

        total_time = 0

        for i, query in enumerate(queries, 1):
            print(f'\n🔍 Query {i}/{len(queries)}: "{query}"')

            # Time the search
            start_time = time.time()
            retrieved = self.kb.search(query, n_results=n_results)
            search_time = time.time() - start_time

            total_time += search_time

            # Check quality
            word_count = len(retrieved.split())
            has_content = word_count > 10

            if has_content:
                results["successful_retrievals"] += 1
                status = "✅"
            else:
                status = "⚠️ "

            print(
                f"   {status} Retrieved: {word_count} words in {search_time * 1000:.1f}ms"
            )
            print(f"   Preview: {retrieved[:150]}...")

            results["query_results"].append(
                {
                    "query": query,
                    "word_count": word_count,
                    "search_time_ms": round(search_time * 1000, 2),
                    "has_content": has_content,
                }
            )

        results["avg_search_time"] = round(total_time / len(queries) * 1000, 2)

        # Summary
        success_rate = results["successful_retrievals"] / len(queries) * 100

        print(f"\n📊 Summary:")
        print(f"   Queries tested: {len(queries)}")
        print(
            f"   Successful: {results['successful_retrievals']}/{len(queries)} ({success_rate:.1f}%)"
        )
        print(f"   Avg search time: {results['avg_search_time']:.2f}ms")

        return results

    def analyze_document_quality(self) -> Dict:
        """Analyze quality of individual documents"""
        print("\n" + "=" * 70)
        print("📋 DOCUMENT QUALITY ANALYSIS")
        print("=" * 70)

        sample = self.kb.collection.get()

        quality_issues = []
        high_quality = []

        for i, (doc_id, doc, metadata) in enumerate(
            zip(sample["ids"], sample["documents"], sample["metadatas"])
        ):
            word_count = len(doc.split())
            source = metadata.get("source", "unknown")

            # Quality checks
            issues = []

            # Check 1: Very short documents
            if word_count < 20:
                issues.append(f"Too short ({word_count} words)")

            # Check 2: Very long chunks (might affect retrieval)
            if word_count > 2000:
                issues.append(f"Too long ({word_count} words)")

            # Check 3: Low OCR confidence (for images)
            if "ocr_confidence" in metadata:
                confidence = float(metadata["ocr_confidence"])
                if confidence < 70:
                    issues.append(f"Low OCR confidence ({confidence:.1f}%)")

            # Check 4: Empty or very sparse content
            if word_count < 5:
                issues.append("Nearly empty")

            if issues:
                quality_issues.append(
                    {
                        "id": doc_id,
                        "source": source,
                        "word_count": word_count,
                        "issues": issues,
                    }
                )
            elif word_count >= 50 and word_count <= 1000:
                high_quality.append(
                    {"id": doc_id, "source": source, "word_count": word_count}
                )

        print(f"\n✅ High Quality Documents: {len(high_quality)}")
        print(f"⚠️  Documents with Issues: {len(quality_issues)}")

        if quality_issues and len(quality_issues) <= 10:
            print(f"\n⚠️  Quality Issues:")
            for item in quality_issues[:10]:
                print(f"   • {item['source']}")
                for issue in item["issues"]:
                    print(f"     - {issue}")

        return {
            "high_quality_count": len(high_quality),
            "issues_count": len(quality_issues),
            "quality_issues": quality_issues,
        }

    def benchmark_performance(self, n_iterations: int = 10) -> Dict:
        """Benchmark search performance"""
        print("\n" + "=" * 70)
        print(f"⚡ PERFORMANCE BENCHMARK ({n_iterations} iterations)")
        print("=" * 70)

        test_query = "What Python skills do I need for finance jobs?"

        times = []

        print(f'\n🔍 Testing query: "{test_query}"')
        print(f"   Running {n_iterations} iterations...")

        for i in range(n_iterations):
            start = time.time()
            self.kb.search(test_query, n_results=3)
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        print(f"\n📊 Results:")
        print(f"   Average: {avg_time:.2f}ms")
        print(f"   Min: {min_time:.2f}ms")
        print(f"   Max: {max_time:.2f}ms")
        print(f"   Std Dev: {(max_time - min_time):.2f}ms")

        # Performance rating
        if avg_time < 50:
            rating = "🚀 Excellent"
        elif avg_time < 100:
            rating = "✅ Good"
        elif avg_time < 200:
            rating = "⚠️  Acceptable"
        else:
            rating = "❌ Needs Optimization"

        print(f"\n   Performance Rating: {rating}")

        return {
            "avg_time_ms": round(avg_time, 2),
            "min_time_ms": round(min_time, 2),
            "max_time_ms": round(max_time, 2),
            "rating": rating,
        }

    def generate_quality_report(self) -> Dict:
        """Generate comprehensive quality report"""
        print("\n" + "=" * 70)
        print("📄 GENERATING COMPREHENSIVE QUALITY REPORT")
        print("=" * 70)

        report = {
            "generated_at": datetime.now().isoformat(),
            "stats": self.analyze_collection_stats(),
            "retrieval_quality": {},
            "document_quality": self.analyze_document_quality(),
            "performance": self.benchmark_performance(),
        }

        # Test each category
        for category in self.test_queries.keys():
            report["retrieval_quality"][category] = self.test_retrieval_quality(
                category
            )

        return report

    def save_report(self, report: Dict, filename: str = "rag_quality_report.json"):
        """Save quality report to file"""
        import json

        report_path = Path("data") / filename
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"\n💾 Report saved: {report_path}")

        # Also save markdown summary
        md_path = report_path.with_suffix(".md")
        self._save_markdown_report(report, md_path)

        print(f"📝 Markdown report: {md_path}")

    def _save_markdown_report(self, report: Dict, filepath: Path):
        """Save markdown version of report"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("# RAG Quality Analysis Report\n\n")
            f.write(f"**Generated**: {report['generated_at']}\n\n")

            # Stats
            f.write("## 📊 Knowledge Base Statistics\n\n")
            stats = report["stats"]
            f.write(f"- **Total Documents**: {stats['total_documents']}\n")
            f.write(f"- **Total Words**: {stats['total_words']:,}\n")
            f.write(f"- **Avg Words/Doc**: {stats['avg_words_per_doc']}\n\n")

            f.write("### By Format\n\n")
            for fmt, count in stats["format_distribution"].items():
                pct = count / stats["total_documents"] * 100
                f.write(f"- **{fmt}**: {count} docs ({pct:.1f}%)\n")

            # Retrieval Quality
            f.write("\n## 🔍 Retrieval Quality\n\n")
            for category, results in report["retrieval_quality"].items():
                success_rate = (
                    results["successful_retrievals"] / results["queries_tested"] * 100
                )
                f.write(f"### {category.title()}\n")
                f.write(f"- Success Rate: {success_rate:.1f}%\n")
                f.write(f"- Avg Search Time: {results['avg_search_time']:.2f}ms\n\n")

            # Performance
            f.write("\n## ⚡ Performance\n\n")
            perf = report["performance"]
            f.write(f"- **Average**: {perf['avg_time_ms']:.2f}ms\n")
            f.write(f"- **Rating**: {perf['rating']}\n\n")

            # Quality
            f.write("\n## 📋 Document Quality\n\n")
            qual = report["document_quality"]
            f.write(f"- **High Quality**: {qual['high_quality_count']} documents\n")
            f.write(f"- **Issues Found**: {qual['issues_count']} documents\n")


# Quick test
if __name__ == "__main__":
    from rag_engine import KnowledgeBase

    print("=" * 70)
    print("📊 RAG QUALITY ANALYZER TEST")
    print("=" * 70)

    # Initialize
    kb = KnowledgeBase()
    analyzer = RAGQualityAnalyzer(kb)

    # Run full analysis
    report = analyzer.generate_quality_report()

    # Save report
    analyzer.save_report(report)

    print("\n" + "=" * 70)
    print("✅ ANALYSIS COMPLETE!")
    print("=" * 70)
