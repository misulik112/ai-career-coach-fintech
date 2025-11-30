"""
File Processor - Load documents for RAG
Week 1 Day 4 - PDF and text file ingestion
"""

import os
from typing import List, Dict


class FileProcessor:
    def __init__(self):
        self.supported_formats = [".txt", ".pdf"]
        print("📄 File Processor initialized")

    def load_text_file(self, filepath: str) -> str:
        """Load plain text file"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            return content
        except Exception as e:
            print(f"⚠️ Error loading {filepath}: {e}")
            return ""

    def load_pdf_file(self, filepath: str) -> str:
        """Load PDF file"""
        try:
            import pdfplumber

            text = ""
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"

            return text.strip()

        except ImportError:
            print("⚠️ pdfplumber not installed. Using fallback.")
            return self._load_pdf_fallback(filepath)
        except Exception as e:
            print(f"⚠️ Error loading PDF {filepath}: {e}")
            return ""

    def _load_pdf_fallback(self, filepath: str) -> str:
        """Fallback PDF loader using pypdf"""
        try:
            from pypdf import PdfReader

            reader = PdfReader(filepath)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"

            return text.strip()

        except Exception as e:
            print(f"⚠️ PDF fallback also failed: {e}")
            return ""

    def load_file(self, filepath: str) -> Dict[str, str]:
        """Load any supported file and return metadata + content"""
        filename = os.path.basename(filepath)
        ext = os.path.splitext(filename)[1].lower()

        if ext not in self.supported_formats:
            print(f"⚠️ Unsupported format: {ext}")
            return None

        # Load content based on type
        if ext == ".txt":
            content = self.load_text_file(filepath)
        elif ext == ".pdf":
            content = self.load_pdf_file(filepath)
        else:
            content = ""

        # Return structured data
        return {
            "filename": filename,
            "filepath": filepath,
            "extension": ext,
            "content": content,
            "word_count": len(content.split()),
        }

    def load_folder(self, folder_path: str) -> List[Dict]:
        """Load all supported files from a folder"""
        if not os.path.exists(folder_path):
            print(f"⚠️ Folder not found: {folder_path}")
            return []

        files_data = []
        for filename in os.listdir(folder_path):
            filepath = os.path.join(folder_path, filename)

            if os.path.isfile(filepath):
                file_data = self.load_file(filepath)
                if file_data and file_data["content"]:
                    files_data.append(file_data)
                    print(f"   ✓ Loaded: {filename} ({file_data['word_count']} words)")

        return files_data


# Quick test
if __name__ == "__main__":
    processor = FileProcessor()

    print("\n--- Testing Job Post Loader ---")
    job_folder = "data/monitored_folders/job_posts"

    files = processor.load_folder(job_folder)

    if files:
        print(f"\n✅ Loaded {len(files)} job description(s)")
        print(f"\nFirst job preview:")
        print(files[0]["content"][:200] + "...")
    else:
        print(f"\n⚠️ No files found in {job_folder}")
        print("Create the sample job file from Step 2!")
