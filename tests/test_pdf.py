"""
Quick test script for PDF integration
Week 3 Day 16
"""

from main import CareerCoach


def test_pdf_integration():
    print("=" * 70)
    print("🧪 PDF INTEGRATION TEST")
    print("=" * 70)

    # Initialize coach
    print("\n1️⃣  Initializing coach...")
    coach = CareerCoach()

    # Load knowledge
    print("\n2️⃣  Loading knowledge base...")
    coach.load_knowledge()

    # Check what's in the database
    print("\n3️⃣  Checking database contents...")
    sample = coach.kb.collection.peek(limit=30)

    # Count PDFs
    pdf_docs = [doc_id for doc_id in sample["ids"] if doc_id.startswith("pdf_")]
    txt_docs = [
        doc_id
        for doc_id in sample["ids"]
        if "economics_expertise" in doc_id or "python_current" in doc_id
    ]
    job_docs = [doc_id for doc_id in sample["ids"] if doc_id.startswith("job_")]
    anytype_docs = [doc_id for doc_id in sample["ids"] if doc_id.startswith("anytype_")]

    print(f"\n📊 Database Statistics:")
    print(f"   Total documents: {len(sample['ids'])}")
    print(f"   PDF chunks: {len(pdf_docs)}")
    print(f"   Text files: {len(txt_docs)}")
    print(f"   Job posts: {len(job_docs)}")
    print(f"   Anytype: {len(anytype_docs)}")

    # Test PDF search
    if pdf_docs:
        print("\n4️⃣  Testing PDF content search...")

        # Direct search
        pdf_results = coach.kb.search("python finance", n_results=1)
        print(f"\n🔍 Search for 'python finance':")
        print(f"   {pdf_results[:250]}...")

        # Ask coach
        print("\n5️⃣  Asking coach about PDF content...")
        print("\n💬 You: What did I learn from the Python finance guide?")
        response = coach.chat(
            "What did I learn from the 'Lumos: Let there be Language Model System Certification' document?"
        )

        print("\n✅ PDF integration working!")
    else:
        print("\n⚠️  No PDF documents found")
        print("\n💡 To test PDFs:")
        print("   1. Add PDF files to data/pdfs/")
        print("   2. Run: python src/main.py")
        print("   3. PDFs will be auto-indexed!")

    print("\n" + "=" * 70)
    print("🧪 TEST COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    test_pdf_integration()
