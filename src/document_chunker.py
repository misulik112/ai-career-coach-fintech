"""
Document Chunker - Smart text splitting for better RAG
Week 2 Day 11 - Heading-aware, semantic chunking
"""

import re
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Chunk:
    """Represents a text chunk with metadata"""

    text: str
    chunk_id: int
    source: str
    start_pos: int
    end_pos: int
    heading: str = ""
    chunk_type: str = "paragraph"  # paragraph, heading, list, code

    def __len__(self):
        return len(self.text)

    def preview(self, length: int = 50) -> str:
        """Get preview of chunk"""
        preview = self.text[:length]
        return preview + "..." if len(self.text) > length else preview


class DocumentChunker:
    """Smart document chunking with heading awareness"""

    def __init__(
        self, chunk_size: int = 500, overlap: int = 50, min_chunk_size: int = 100
    ):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.min_chunk_size = min_chunk_size

        print(f"📄 Document Chunker initialized")
        print(f"   Chunk size: {chunk_size} chars")
        print(f"   Overlap: {overlap} chars")

    def chunk_by_markdown_headings(self, text: str, source: str = "") -> List[Chunk]:
        """Split by markdown headings (#, ##, ###)"""
        chunks = []
        chunk_id = 0

        # Split by markdown headings
        heading_pattern = r"^(#{1,6})\s+(.+)$"
        lines = text.split("\n")

        current_heading = ""
        current_section = []
        current_pos = 0

        for line in lines:
            match = re.match(heading_pattern, line, re.MULTILINE)

            if match:
                # Save previous section
                if current_section:
                    section_text = "\n".join(current_section)

                    # Create chunks from this section
                    section_chunks = self._split_large_section(
                        section_text, source, current_heading, current_pos, chunk_id
                    )
                    chunks.extend(section_chunks)
                    chunk_id += len(section_chunks)

                # Start new section
                current_heading = match.group(2)
                current_section = [line]
                current_pos += len("\n".join(lines[: lines.index(line)]))
            else:
                current_section.append(line)

        # Handle last section
        if current_section:
            section_text = "\n".join(current_section)
            section_chunks = self._split_large_section(
                section_text, source, current_heading, current_pos, chunk_id
            )
            chunks.extend(section_chunks)

        return chunks

    def _split_large_section(
        self, text: str, source: str, heading: str, start_pos: int, chunk_id_start: int
    ) -> List[Chunk]:
        """Split large sections into smaller chunks"""
        chunks = []

        # If section is small enough, keep as one chunk
        if len(text) <= self.chunk_size:
            chunk = Chunk(
                text=text,
                chunk_id=chunk_id_start,
                source=source,
                start_pos=start_pos,
                end_pos=start_pos + len(text),
                heading=heading,
                chunk_type="section",
            )
            return [chunk]

        # Split by sentences for larger sections
        sentences = self._split_into_sentences(text)

        current_chunk = []
        current_length = 0
        chunk_id = chunk_id_start
        pos = start_pos

        for sentence in sentences:
            sentence_len = len(sentence)

            # Check if adding this sentence exceeds chunk size
            if current_length + sentence_len > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = " ".join(current_chunk)
                chunk = Chunk(
                    text=chunk_text,
                    chunk_id=chunk_id,
                    source=source,
                    start_pos=pos,
                    end_pos=pos + len(chunk_text),
                    heading=heading,
                )
                chunks.append(chunk)

                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk)
                current_chunk = [overlap_text, sentence] if overlap_text else [sentence]
                current_length = len(overlap_text) + sentence_len
                chunk_id += 1
                pos += len(chunk_text) - len(overlap_text)
            else:
                current_chunk.append(sentence)
                current_length += sentence_len

        # Save final chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunk = Chunk(
                text=chunk_text,
                chunk_id=chunk_id,
                source=source,
                start_pos=pos,
                end_pos=pos + len(chunk_text),
                heading=heading,
            )
            chunks.append(chunk)

        return chunks

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences (simple version)"""
        # Simple sentence splitter (can be improved with NLP)
        sentence_endings = r"[.!?]+[\s\n]+"
        sentences = re.split(sentence_endings, text)

        # Clean and filter
        sentences = [s.strip() for s in sentences if s.strip()]

        return sentences

    def _get_overlap_text(self, sentences: List[str]) -> str:
        """Get last N characters for overlap"""
        if not sentences:
            return ""

        # Get last sentence(s) up to overlap size
        overlap_text = ""
        for sentence in reversed(sentences):
            if len(overlap_text) + len(sentence) <= self.overlap:
                overlap_text = sentence + " " + overlap_text
            else:
                break

        return overlap_text.strip()

    def chunk_simple(self, text: str, source: str = "") -> List[Chunk]:
        """Simple fixed-size chunking (baseline comparison)"""
        chunks = []
        chunk_id = 0

        for i in range(0, len(text), self.chunk_size - self.overlap):
            chunk_text = text[i : i + self.chunk_size]

            if len(chunk_text) < self.min_chunk_size and chunks:
                # Merge small final chunk with previous
                chunks[-1].text += " " + chunk_text
                chunks[-1].end_pos += len(chunk_text)
            else:
                chunk = Chunk(
                    text=chunk_text,
                    chunk_id=chunk_id,
                    source=source,
                    start_pos=i,
                    end_pos=i + len(chunk_text),
                    chunk_type="simple",
                )
                chunks.append(chunk)
                chunk_id += 1

        return chunks

    def measure_quality(self, chunks: List[Chunk]) -> Dict:
        """Measure chunking quality metrics"""
        if not chunks:
            return {}

        chunk_sizes = [len(c) for c in chunks]

        # Count chunks that cut mid-sentence (simple heuristic)
        bad_cuts = 0
        for chunk in chunks:
            if chunk.text and not chunk.text[-1] in ".!?\n":
                bad_cuts += 1

        return {
            "total_chunks": len(chunks),
            "avg_chunk_size": sum(chunk_sizes) / len(chunks),
            "min_chunk_size": min(chunk_sizes),
            "max_chunk_size": max(chunk_sizes),
            "bad_cuts": bad_cuts,
            "bad_cut_rate": bad_cuts / len(chunks) * 100,
            "chunks_with_headings": sum(1 for c in chunks if c.heading),
        }


# Quick test
if __name__ == "__main__":
    chunker = DocumentChunker(chunk_size=300, overlap=50)

    # Test document
    test_doc = """# Python for Finance

## Introduction
Python is excellent for financial analysis. It has powerful libraries like Pandas and NumPy that make data manipulation easy.

## Key Libraries
Pandas is used for data frames. NumPy handles numerical operations. Matplotlib creates visualizations.

## Use Cases
You can build trading algorithms, risk models, and automated reports. Python is the standard in FinTech.

## Getting Started
Install the libraries with pip. Start with simple data analysis. Build portfolio projects to demonstrate skills."""

    print("\n--- Testing Heading-Aware Chunking ---")
    chunks = chunker.chunk_by_markdown_headings(test_doc, "test.md")

    print(f"\n✅ Created {len(chunks)} chunks:\n")
    for chunk in chunks:
        print(f"Chunk {chunk.chunk_id} (Heading: '{chunk.heading}'):")
        print(f"  {chunk.preview(80)}")
        print(f"  Length: {len(chunk)} chars\n")

    # Compare with simple chunking
    print("\n--- Comparing with Simple Chunking ---")
    simple_chunks = chunker.chunk_simple(test_doc, "test.md")

    print(f"\nHeading-aware quality:")
    print(chunker.measure_quality(chunks))

    print(f"\nSimple chunking quality:")
    print(chunker.measure_quality(simple_chunks))
