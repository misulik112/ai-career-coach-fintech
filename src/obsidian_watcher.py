"""
Obsidian Vault Watcher - Multi-handler orchestration
Week 2 Day 8
"""

import os
import time
from watchdog.observers import Observer
from rag_engine import KnowledgeBase
from obsidian_handlers import (
    ObsidianDailyNoteHandler,
    ObsidianResearchHandler,
    ObsidianSkillHandler,
)


class ObsidianVaultWatcher:
    """Watch Obsidian vault with specialized handlers per folder"""

    def __init__(self, vault_path: str):
        self.vault_path = vault_path
        self.kb = KnowledgeBase()
        self.observer = Observer()

        # Create specialized handlers
        self.handlers = {
            "daily": ObsidianDailyNoteHandler(self.kb),
            "research": ObsidianResearchHandler(self.kb),
            "skills": ObsidianSkillHandler(self.kb),
        }

        print(f"🗂️  Obsidian Vault Watcher initialized")
        print(f"   Vault: {vault_path}")

    def start(self):
        """Start watching vault folders"""
        folders_watched = 0

        for folder_name, handler in self.handlers.items():
            folder_path = os.path.join(self.vault_path, folder_name)

            # Resolve symlink to real path
            real_path = os.path.realpath(folder_path)

            if os.path.exists(real_path):
                self.observer.schedule(handler, real_path, recursive=False)
                print(f"   👁️  Watching: {folder_name}/ -> {real_path}")
                folders_watched += 1
            else:
                print(f"   ⚠️ Folder not found: {folder_name}/ (create it!)")

        if folders_watched == 0:
            print("\n⚠️ No folders found! Check vault path.")
            return False

        self.observer.start()
        print(f"\n✅ Watching {folders_watched} folder(s)")
        print("   Write Obsidian notes to see real-time tracking...")
        print("   Press Ctrl+C to stop\n")
        return True

    def stop(self):
        """Stop watching"""
        self.observer.stop()
        self.observer.join()
        print("\n🛑 Obsidian Watcher stopped")


# Test mode
if __name__ == "__main__":
    # UPDATE THIS PATH to your actual Obsidian vault
    VAULT_PATH = "data/obsidian_vault"  # or "/path/to/career-coach-build"

    # Create test folders if needed
    os.makedirs(f"{VAULT_PATH}/daily", exist_ok=True)
    os.makedirs(f"{VAULT_PATH}/research", exist_ok=True)
    os.makedirs(f"{VAULT_PATH}/skills", exist_ok=True)

    watcher = ObsidianVaultWatcher(VAULT_PATH)

    if watcher.start():
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            watcher.stop()
