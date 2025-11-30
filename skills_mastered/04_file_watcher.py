"""
SKILL MASTERED: Real-Time File Monitoring with Watchdog
Week 1 Day 5

What I learned:
- File system event handling (create, modify, delete)
- Observer pattern implementation
- Real-time data pipeline updates
- Async event processing

Portfolio highlight:
"Built real-time knowledge ingestion pipeline - drop documents into folders,
automatically indexed in vector database within seconds"

Business value:
- Zero-friction user experience (drag-and-drop workflow)
- Always up-to-date knowledge base
- Scalable monitoring (handles multiple folders simultaneously)

Technical details:
- Watchdog library for cross-platform file monitoring
- Event classification (jobs vs skills vs logs)
- Auto-cleanup on deletion
- Debouncing for file write completion
"""

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time


class SimpleHandler(FileSystemEventHandler):
    def on_created(self, event):
        print(f"Created: {event.src_path}")


def demo():
    """Quick demo of file watching"""
    observer = Observer()
    observer.schedule(SimpleHandler(), ".", recursive=False)
    observer.start()

    try:
        time.sleep(5)  # Watch for 5 seconds
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    demo()
