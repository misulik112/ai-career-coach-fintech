"""
File Watcher - Real-time monitoring of knowledge folders
Week 1 Day 5 - Auto-update RAG when files change
"""

import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rag_engine import KnowledgeBase
from file_processor import FileProcessor


class CareerKnowledgeHandler(FileSystemEventHandler):
    """Handles file system events for career knowledge folders"""

    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        self.processor = FileProcessor()
        print("👁️  File Watcher Handler initialized")

    def on_created(self, event):
        """Called when a file is created"""
        if event.is_directory:
            return

        filepath = event.src_path
        filename = os.path.basename(filepath)

        # Ignore system files
        if filename.startswith("."):
            return

        print(f"\n📥 NEW FILE DETECTED: {filename}")
        self._process_file(filepath, action="created")

    def on_modified(self, event):
        """Called when a file is modified"""
        if event.is_directory:
            return

        filepath = event.src_path
        filename = os.path.basename(filepath)

        if filename.startswith("."):
            return

        print(f"\n✏️  FILE UPDATED: {filename}")
        self._process_file(filepath, action="updated")

    def on_deleted(self, event):
        """Called when a file is deleted"""
        if event.is_directory:
            return

        filepath = event.src_path
        filename = os.path.basename(filepath)

        if filename.startswith("."):
            return

        print(f"\n🗑️  FILE DELETED: {filename}")

        # Remove from vector DB
        doc_id = self._get_doc_id(filename, filepath)
        try:
            self.kb.collection.delete(ids=[doc_id])
            print(f"   ✓ Removed from knowledge base")
        except Exception as e:
            print(f"   ⚠️ Deletion note: {e}")

    def _process_file(self, filepath: str, action: str):
        """Process file and update knowledge base"""
        # Wait a moment for file write to complete
        time.sleep(0.5)

        # Load file
        file_data = self.processor.load_file(filepath)

        if not file_data or not file_data["content"]:
            print(f"   ⚠️ Could not process file")
            return

        # Determine document type
        doc_type = self._classify_document(filepath, file_data["content"])

        # Generate document ID
        doc_id = self._get_doc_id(file_data["filename"], filepath)

        # Upsert to vector DB
        try:
            self.kb.collection.upsert(
                documents=[file_data["content"]],
                ids=[doc_id],
                metadatas=[
                    {
                        "source": file_data["filename"],
                        "type": doc_type,
                        "word_count": file_data["word_count"],
                        "action": action,
                    }
                ],
            )

            print(f"   ✓ Indexed as '{doc_type}' ({file_data['word_count']} words)")
            print(
                f"   💾 Knowledge base now has {self.kb.collection.count()} documents"
            )

        except Exception as e:
            print(f"   ⚠️ Indexing error: {e}")

    def _classify_document(self, filepath: str, content: str) -> str:
        """Classify document type based on path and content"""
        path_lower = filepath.lower()
        content_lower = content.lower()

        if (
            "job_posts" in path_lower
            or "job title" in content_lower
            or "requirements:" in content_lower
        ):
            return "job_description"
        elif "skills" in path_lower or "expertise" in content_lower:
            return "skill_inventory"
        elif "goals" in content_lower or "transition" in content_lower:
            return "career_goals"
        elif "learning" in content_lower or "log" in path_lower:
            return "learning_log"
        else:
            return "general_knowledge"

    def _get_doc_id(self, filename: str, filepath: str) -> str:
        """Generate consistent document ID"""
        # Use path to differentiate same filename in different folders
        if "job_posts" in filepath:
            prefix = "job_"
        elif "skills" in filepath:
            prefix = "skill_"
        else:
            prefix = "doc_"

        # Clean filename
        clean_name = filename.replace(".txt", "").replace(".pdf", "").replace(" ", "_")
        return f"{prefix}{clean_name}"


class FileWatcher:
    """Main file watcher orchestrator"""

    def __init__(self, watch_paths: list):
        self.watch_paths = watch_paths
        self.kb = KnowledgeBase()
        self.observer = Observer()

        # Setup event handler
        self.handler = CareerKnowledgeHandler(self.kb)

        print("🔍 File Watcher initialized")
        print(f"   Monitoring {len(watch_paths)} folder(s)")

    def start(self):
        """Start watching folders"""
        # Schedule monitoring for each path
        for path in self.watch_paths:
            if os.path.exists(path):
                self.observer.schedule(self.handler, path, recursive=False)
                print(f"   👁️  Watching: {path}")
            else:
                print(f"   ⚠️ Path not found: {path}")

        # Start observer
        self.observer.start()
        print("\n✅ File Watcher is ACTIVE!")
        print("   Drop files into monitored folders to see real-time updates...")
        print("   Press Ctrl+C to stop\n")

    def stop(self):
        """Stop watching"""
        self.observer.stop()
        self.observer.join()
        print("\n🛑 File Watcher stopped")


# Test mode
if __name__ == "__main__":
    # Paths to monitor
    watch_folders = ["data/monitored_folders/job_posts", "data/knowledge_base/skills"]

    # Create watcher
    watcher = FileWatcher(watch_folders)

    try:
        # Start monitoring
        watcher.start()

        # Keep running
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        watcher.stop()
