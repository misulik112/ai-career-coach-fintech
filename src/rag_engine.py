"""
RAG (Retrieval Augmented Generation) Engine
Week 1 Day 3 - Your personal knowledge base brain
"""

import os
from pathlib import Path
import chromadb
from document_chunker import DocumentChunker
from document_cache import DocumentCache
from config import Config


class KnowledgeBase:
    # Vector database for RAG

    def __init__(self, kb_path="data/knowledge_base"):
        self.kb_path = Config.KNOWLEDGE_BASE_PATH
        db_path = Config.CHROMA_DB_PATH
        collection_name = (
            Config.CHROMA_COLLECTION_NAME
            if hasattr(Config, "CHROMA_COLLECTION_NAME")
            else "career_knowledge"
        )

        # Initialize ChromaDB (NEW API)
        self.client = chromadb.PersistentClient(path=db_path)

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="career_knowledge",
            metadata={"description": "Economist skills and transition goals"},
        )

        # Initialize document chunker
        self.chunker = DocumentChunker(chunk_size=500, overlap=50)

        # Initialize document cache
        self.doc_cache = DocumentCache()
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

    def load_job_posts(self, folder_path="data/monitored_folders/job_posts"):
        """Load job descriptions from folder"""
        from file_processor import FileProcessor

        processor = FileProcessor()
        job_files = processor.load_folder(folder_path)

        if not job_files:
            print("⚠️ No job posts found")
            return

        jobs_loaded = 0
        for job_data in job_files:
            # Add to vector database
            doc_id = (
                f"job_{job_data['filename'].replace('.txt', '').replace('.pdf', '')}"
            )

            self.collection.upsert(
                documents=[job_data["content"]],
                ids=[doc_id],
                metadatas=[
                    {
                        "source": job_data["filename"],
                        "type": "job_description",
                        "word_count": job_data["word_count"],
                    }
                ],
            )

            jobs_loaded += 1
            print(f"   ✓ Indexed: {job_data['filename']}")

        print(f"\n✅ Loaded {jobs_loaded} job post(s) into vector DB")

    def add_document_with_chunks(self, filepath: str, doc_type: str = "general"):
        """Add document with smart chunking"""
        from file_processor import FileProcessor

        processor = FileProcessor()
        file_data = processor.load_file(filepath)

        if not file_data or not file_data["content"]:
            return

        # Create chunks
        chunks = self.chunker.chunk_by_markdown_headings(
            file_data["content"], file_data["filename"]
        )

        print(f"\n📄 Processing: {file_data['filename']}")
        print(f"   Created {len(chunks)} smart chunks")

        # Add each chunk to vector DB
        for chunk in chunks:
            doc_id = f"{doc_type}_{file_data['filename']}_{chunk.chunk_id}"

            self.collection.upsert(
                documents=[chunk.text],
                ids=[doc_id],
                metadatas=[
                    {
                        "source": file_data["filename"],
                        "type": doc_type,
                        "chunk_id": chunk.chunk_id,
                        "heading": chunk.heading,
                        "chunk_type": chunk.chunk_type,
                    }
                ],
            )

        # Measure quality
        quality = self.chunker.measure_quality(chunks)
        print(f"   Quality: {quality['bad_cut_rate']:.1f}% bad cuts")

        return chunks

    def load_pdfs(self, folder_path="data/pdfs"):
        """Load PDF documents with caching"""
        from pdf_parser import PDFParser

        parser = PDFParser()
        folder = Path(folder_path)

        if not folder.exists():
            print(f"⚠️  Folder not found: {folder_path}")
            return

        pdf_files = list(folder.glob("**/*.pdf"))

        if not pdf_files:
            print("⚠️  No PDF files found")
            return

        pdfs_loaded = 0
        pdfs_from_cache = 0

        for pdf_file in pdf_files:
            # Try cache first
            cached_data = self.doc_cache.get(pdf_file)

            if cached_data:
                # Use cached data
                pdf_data = cached_data
                pdfs_from_cache += 1
            else:
                # Parse fresh
                pdf_data = parser.parse_file(pdf_file)

                if pdf_data:
                    # Cache for next time
                    self.doc_cache.set(pdf_file, pdf_data)
                else:
                    continue

            # Add to vector DB (same as before)
            if pdf_data["word_count"] > 500:
                chunks = self.chunker.chunk_simple(
                    pdf_data["content"], pdf_data["filename"]
                )

                for chunk in chunks:
                    doc_id = f"pdf_{pdf_data['filename']}_{chunk.chunk_id}"

                    self.collection.upsert(
                        documents=[chunk.text],
                        ids=[doc_id],
                        metadatas=[
                            {
                                "source": pdf_data["filename"],
                                "type": "pdf_document",
                                "chunk_id": chunk.chunk_id,
                                "page_count": str(pdf_data["page_count"]),
                                "title": pdf_data["metadata"].get("title", ""),
                            }
                        ],
                    )

                if not cached_data:
                    print(f"\n📄 Processing: {pdf_data['filename']}")
                    print(f"   Created {len(chunks)} chunks")
            else:
                doc_id = f"pdf_{pdf_data['filename']}"

                self.collection.upsert(
                    documents=[pdf_data["content"]],
                    ids=[doc_id],
                    metadatas=[
                        {
                            "source": pdf_data["filename"],
                            "type": "pdf_document",
                            "page_count": str(pdf_data["page_count"]),
                            "word_count": str(pdf_data["word_count"]),
                            "title": pdf_data["metadata"].get("title", ""),
                        }
                    ],
                )

                if not cached_data:
                    print(f"   ✓ Indexed: {pdf_data['filename']}")

            pdfs_loaded += 1

        print(f"\n✅ Loaded {pdfs_loaded} PDF(s) ({pdfs_from_cache} from cache)")

    def load_docx(self, folder_path="data/docx"):
        """Load Word documents with caching"""
        from docx_parser import DOCXParser

        parser = DOCXParser()
        folder = Path(folder_path)

        if not folder.exists():
            print(f"⚠️  Folder not found: {folder_path}")
            return

        docx_files = [
            f for f in folder.glob("**/*.docx") if not f.name.startswith("~$")
        ]

        if not docx_files:
            print("⚠️  No DOCX files found")
            return

        docx_loaded = 0
        docx_from_cache = 0

        for docx_file in docx_files:
            # Try cache first
            cached_data = self.doc_cache.get(docx_file)

            if cached_data:
                docx_data = cached_data
                docx_from_cache += 1
            else:
                docx_data = parser.parse_file(docx_file)

                if docx_data:
                    self.doc_cache.set(docx_file, docx_data)
                else:
                    continue

            # Add to vector DB (same chunking logic as before)
            if docx_data["word_count"] > 500:
                chunks = self.chunker.chunk_simple(
                    docx_data["content"], docx_data["filename"]
                )

                for chunk in chunks:
                    doc_id = f"docx_{docx_data['filename']}_{chunk.chunk_id}"

                    self.collection.upsert(
                        documents=[chunk.text],
                        ids=[doc_id],
                        metadatas=[
                            {
                                "source": docx_data["filename"],
                                "type": "docx_document",
                                "chunk_id": chunk.chunk_id,
                                "title": docx_data["metadata"].get("title", ""),
                                "author": docx_data["metadata"].get("author", ""),
                            }
                        ],
                    )

                if not cached_data:
                    print(f"\n📝 Processing: {docx_data['filename']}")
                    print(f"   Created {len(chunks)} chunks")
            else:
                doc_id = f"docx_{docx_data['filename']}"

                self.collection.upsert(
                    documents=[docx_data["content"]],
                    ids=[doc_id],
                    metadatas=[
                        {
                            "source": docx_data["filename"],
                            "type": "docx_document",
                            "word_count": str(docx_data["word_count"]),
                            "title": docx_data["metadata"].get("title", ""),
                        }
                    ],
                )

                if not cached_data:
                    print(f"   ✓ Indexed: {docx_data['filename']}")

            docx_loaded += 1

        print(f"\n✅ Loaded {docx_loaded} DOCX file(s) ({docx_from_cache} from cache)")

    def load_images(
        self, folder_path="data/images", min_words=5, lang="eng", auto_detect=False
    ):
        """Load images with OCR (with caching)"""
        from image_ocr import ImageOCR

        ocr = ImageOCR(default_lang=lang)
        folder = Path(folder_path)

        if not folder.exists():
            print("⚠️  No images folder found")
            return

        image_extensions = ["*.png", "*.jpg", "*.jpeg", "*.gif", "*.bmp"]
        image_files = []

        for ext in image_extensions:
            image_files.extend(folder.glob(f"**/{ext}"))

        if not image_files:
            print("⚠️  No images found")
            return

        images_loaded = 0
        images_from_cache = 0

        for img_file in image_files:
            # Try cache first
            cached_data = self.doc_cache.get(img_file)

            if cached_data:
                img_data = cached_data
                images_from_cache += 1
            else:
                img_data = ocr.extract_text_from_image(
                    img_file, lang=lang, auto_detect=auto_detect
                )

                if img_data:
                    self.doc_cache.set(img_file, img_data)
                else:
                    continue

            # Skip low-content images
            if img_data["word_count"] < min_words:
                continue

            # Add to vector DB
            doc_id = f"image_{img_data['filename']}"

            self.collection.upsert(
                documents=[img_data["content"]],
                ids=[doc_id],
                metadatas=[
                    {
                        "source": img_data["filename"],
                        "type": "image_ocr",
                        "word_count": str(img_data["word_count"]),
                        "ocr_language": img_data["metadata"]["ocr_language"],
                        "ocr_confidence": str(img_data["metadata"]["ocr_confidence"]),
                    }
                ],
            )

            images_loaded += 1

            if not cached_data:
                print(f"   ✓ Indexed: {img_data['filename']}")

        print(f"\n✅ Loaded {images_loaded} image(s) ({images_from_cache} from cache)")


# Quick test
if __name__ == "__main__":
    kb = KnowledgeBase()

    print("\n--- Loading Knowledge Files ---")
    kb.load_knowledge_files()

    print("\n--- Loading Job Posts ---")
    kb.load_job_posts()

    print("\n--- Testing Job Search ---")
    query = "What Python skills are required?"
    print(f"Query: {query}\n")
    context = kb.search(query, n_results=1)
    print(f"Found:\n{context[:400]}...")

    kb.get_stats()
