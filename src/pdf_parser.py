"""
PDF Parser for Research Papers and Documents
Week 3 Day 16 - Extract text and metadata from PDFs
"""

from typing import Dict, Optional, List
from pathlib import Path
import re

try:
    import PyPDF2
    import pdfplumber

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️  PDF libraries not installed. Run: pip install PyPDF2 pdfplumber")


class PDFParser:
    """Extract text and metadata from PDF files"""

    def __init__(self):
        self.stats = {
            "files_processed": 0,
            "pages_extracted": 0,
            "extraction_method": "hybrid",  # PyPDF2 + pdfplumber
        }

        print(f"📄 PDF Parser initialized")
        print(f"   Available: {PDF_AVAILABLE}")

    def parse_file(self, filepath: str) -> Optional[Dict]:
        """Parse a PDF file and extract content + metadata"""
        if not PDF_AVAILABLE:
            print("❌ PDF libraries not available")
            return None

        filepath = Path(filepath)

        if not filepath.exists():
            print(f"❌ File not found: {filepath}")
            return None

        if filepath.suffix.lower() != ".pdf":
            print(f"❌ Not a PDF file: {filepath}")
            return None

        print(f"\n📄 Parsing PDF: {filepath.name}")

        # Try PyPDF2 first (faster, works for most PDFs)
        content = self._extract_with_pypdf2(filepath)

        # If PyPDF2 fails or returns empty, try pdfplumber
        if not content or len(content.strip()) < 50:
            print("   ℹ️  PyPDF2 returned minimal text, trying pdfplumber...")
            content = self._extract_with_pdfplumber(filepath)

        # Extract metadata
        metadata = self._extract_metadata(filepath)

        # Get page count
        page_count = self._get_page_count(filepath)

        # Word count
        word_count = len(content.split())

        result = {
            "filename": filepath.name,
            "filepath": str(filepath),
            "content": content,
            "metadata": metadata,
            "page_count": page_count,
            "word_count": word_count,
            "file_type": "pdf",
        }

        print(f"   ✓ Extracted: {word_count} words from {page_count} pages")

        self.stats["files_processed"] += 1
        self.stats["pages_extracted"] += page_count

        return result

    def _extract_with_pypdf2(self, filepath: Path) -> str:
        """Extract text using PyPDF2 (fast, basic)"""
        try:
            content_parts = []

            with open(filepath, "rb") as file:
                reader = PyPDF2.PdfReader(file)

                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        content_parts.append(text)

            content = "\n\n".join(content_parts)

            if content and len(content.strip()) > 50:
                print(f"   ✓ PyPDF2: {len(content)} chars")

            return content

        except Exception as e:
            print(f"   ⚠️  PyPDF2 failed: {e}")
            return ""

    def _extract_with_pdfplumber(self, filepath: Path) -> str:
        """Extract text using pdfplumber (better layout preservation)"""
        try:
            content_parts = []

            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    # Extract text with layout
                    text = page.extract_text(layout=True)

                    if text:
                        content_parts.append(text)

                    # Also try to extract tables
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            # Convert table to text
                            table_text = self._table_to_text(table)
                            content_parts.append(f"\n[TABLE]\n{table_text}\n")

            content = "\n\n".join(content_parts)

            if content:
                print(f"   ✓ pdfplumber: {len(content)} chars")

            return content

        except Exception as e:
            print(f"   ⚠️  pdfplumber failed: {e}")
            return ""

    def _table_to_text(self, table: List[List]) -> str:
        """Convert table data to readable text"""
        if not table:
            return ""

        # Simple table formatting
        rows = []
        for row in table:
            # Filter out None values
            clean_row = [str(cell) if cell else "" for cell in row]
            rows.append(" | ".join(clean_row))

        return "\n".join(rows)

    def _extract_metadata(self, filepath: Path) -> Dict:
        """Extract PDF metadata (title, author, etc.)"""
        metadata = {
            "filename": filepath.name,
            "source": "pdf",
            "title": filepath.stem.replace("-", " ").replace("_", " ").title(),
        }

        try:
            with open(filepath, "rb") as file:
                reader = PyPDF2.PdfReader(file)

                if reader.metadata:
                    # Extract standard PDF metadata
                    if reader.metadata.title:
                        metadata["title"] = reader.metadata.title
                    if reader.metadata.author:
                        metadata["author"] = reader.metadata.author
                    if reader.metadata.subject:
                        metadata["subject"] = reader.metadata.subject
                    if reader.metadata.creator:
                        metadata["creator"] = reader.metadata.creator
                    if reader.metadata.producer:
                        metadata["producer"] = reader.metadata.producer

                    # Creation date
                    if (
                        hasattr(reader.metadata, "creation_date")
                        and reader.metadata.creation_date
                    ):
                        metadata["created"] = str(reader.metadata.creation_date)

        except Exception as e:
            print(f"   ℹ️  Could not extract metadata: {e}")

        return metadata

    def _get_page_count(self, filepath: Path) -> int:
        """Get number of pages in PDF"""
        try:
            with open(filepath, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                return len(reader.pages)
        except:
            return 0

    def parse_folder(self, folder_path: str) -> List[Dict]:
        """Parse all PDFs in a folder"""
        folder = Path(folder_path)

        if not folder.exists():
            print(f"❌ Folder not found: {folder_path}")
            return []

        pdf_files = list(folder.glob("**/*.pdf"))

        if not pdf_files:
            print(f"⚠️  No PDF files found in {folder_path}")
            return []

        print(f"\n📂 Found {len(pdf_files)} PDF file(s)")

        results = []
        for pdf_file in pdf_files:
            result = self.parse_file(pdf_file)
            if result:
                results.append(result)

        return results

    def get_stats(self) -> Dict:
        """Get parsing statistics"""
        return {
            **self.stats,
            "avg_pages_per_file": (
                self.stats["pages_extracted"] / self.stats["files_processed"]
                if self.stats["files_processed"] > 0
                else 0
            ),
        }

    def print_stats(self):
        """Print parsing statistics"""
        stats = self.get_stats()

        print(f"\n📊 PDF Parser Statistics:")
        print(f"   Files processed: {stats['files_processed']}")
        print(f"   Pages extracted: {stats['pages_extracted']}")
        print(f"   Avg pages/file: {stats['avg_pages_per_file']:.1f}")


# Quick test
if __name__ == "__main__":
    print("=" * 70)
    print("📄 PDF PARSER TEST")
    print("=" * 70)

    parser = PDFParser()

    if not PDF_AVAILABLE:
        print("\n❌ Install PDF libraries first:")
        print("   pip install PyPDF2 pdfplumber")
    else:
        # Test with a sample PDF if available
        import os

        test_folder = "data/pdfs"

        if not os.path.exists(test_folder):
            os.makedirs(test_folder, exist_ok=True)
            print(f"\n📁 Created folder: {test_folder}")
            print(f"   Add some PDF files here to test!")
            print(f"\n💡 You can add:")
            print(f"   • Research papers (arXiv, Google Scholar)")
            print(f"   • Job descriptions (save as PDF)")
            print(f"   • Financial reports")
            print(f"   • Python tutorials")
        else:
            # Parse all PDFs in folder
            results = parser.parse_folder(test_folder)

            if results:
                print(f"\n✅ Parsed {len(results)} PDF(s)")

                # Show first result preview
                print(f"\n--- Sample: {results[0]['filename']} ---")
                print(f"Title: {results[0]['metadata'].get('title', 'N/A')}")
                print(f"Pages: {results[0]['page_count']}")
                print(f"Words: {results[0]['word_count']}")
                print(f"\nContent preview:")
                print(results[0]["content"][:300] + "...")

            parser.print_stats()

    print("\n" + "=" * 70)
    print("✅ PDF PARSER READY!")
    print("=" * 70)
