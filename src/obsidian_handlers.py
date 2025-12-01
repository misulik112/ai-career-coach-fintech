"""
Obsidian-specific event handlers
Week 2 Day 8 - Different logic per folder
"""

from os.path import join
from watchdog.events import FileSystemEventHandler
from markdown_parser import MarkdownParser
from rag_engine import KnowledgeBase
import os
import time


class ObsidianDailyNoteHandler(FileSystemEventHandler):
    """Handler for daily notes - tracks learning progress"""

    def __init__(self, kb: KnowledgeBase):
        super().__init__()  # For symlinked folders
        self.kb = kb
        self.parser = MarkdownParser()
        print("📅 Daily Note Handler initialized")

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(".md"):
            return

        print(f"\n📅 NEW DAILY NOTE: {os.path.basename(event.src_path)}")
        self._process_daily_note(event.src_path)

    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith(".md"):
            return

        print(f"\n✏️  DAILY NOTE UPDATED: {os.path.basename(event.src_path)}")
        self._process_daily_note(event.src_path)

    def _process_daily_note(self, filepath: str):
        """Process daily note and extract learning"""
        time.sleep(0.5)  # Wait for file write

        parsed = self.parser.parse_file(filepath)
        if not parsed:
            return

        # Extract key information
        skills_learned = self.parser.extract_skills(parsed)
        metadata = parsed.get("metadata", {})

        # Build summary
        summary = f"Daily Note: {parsed['filename']}\n"
        summary += f"Date: {metadata.get('date', 'unknown')}\n"

        if skills_learned:
            summary += f"Skills practiced: {', '.join(skills_learned)}\n"

        summary += f"\nContent:\n{parsed['content']}"

        # Add to knowledge base
        doc_id = f"daily_{parsed['filename'].replace('.md', '')}"

        self.kb.collection.upsert(
            documents=[summary],
            ids=[doc_id],
            metadatas=[
                {
                    "source": parsed["filename"],
                    "type": "daily_note",
                    "date": str(metadata.get("date", "")),
                    "skills": ", ".join(skills_learned) if skills_learned else "",
                    "tags": ", ".join(parsed["tags"]) if parsed["tags"] else "",
                }
            ],
        )

        print(f"   ✓ Tracked learning: {len(skills_learned)} skills")
        if skills_learned:
            print(f"      Skills: {', '.join(skills_learned)}")


class ObsidianResearchHandler(FileSystemEventHandler):
    """Handler for research notes - market intelligence"""

    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        self.parser = MarkdownParser()
        print("🔍 Research Handler initialized")

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(".md"):
            return

        print(f"\n🔍 NEW RESEARCH: {os.path.basename(event.src_path)}")
        self._process_research(event.src_path)

    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith(".md"):
            return

        print(f"\n✏️  RESEARCH UPDATED: {os.path.basename(event.src_path)}")
        self._process_research(event.src_path)

    def _process_research(self, filepath: str):
        """Process research note"""
        time.sleep(0.5)

        parsed = self.parser.parse_file(filepath)
        if not parsed:
            return

        metadata = parsed.get("metadata", {})

        # Add context
        enhanced_content = f"Research: {parsed['filename']}\n"
        enhanced_content += f"Topic: {metadata.get('topic', 'general')}\n"
        enhanced_content += f"Source: {metadata.get('source', 'unknown')}\n\n"
        enhanced_content += parsed["content"]

        doc_id = f"research_{parsed['filename'].replace('.md', '').replace(' ', '_')}"

        self.kb.collection.upsert(
            documents=[enhanced_content],
            ids=[doc_id],
            metadatas=[
                {
                    "source": parsed["filename"],
                    "type": "research",
                    "topic": ", ".join(metadata.get("topic", []))
                    if isinstance(metadata.get("topic"), list)
                    else str(metadata.get("topic", "")),
                    "tags": ", ".join(parsed["tags"]) if parsed["tags"] else "",
                }
            ],
        )

        print(f"   ✓ Indexed as market intelligence")


class ObsidianSkillHandler(FileSystemEventHandler):
    """Handler for skill notes - proficiency tracking"""

    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        self.parser = MarkdownParser()
        print("🎯 Skill Handler initialized")

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(".md"):
            return

        print(f"\n🎯 NEW SKILL NOTE: {os.path.basename(event.src_path)}")
        self._process_skill(event.src_path)

    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith(".md"):
            return

        print(f"\n✏️  SKILL UPDATED: {os.path.basename(event.src_path)}")
        self._process_skill(event.src_path)

    def _process_skill(self, filepath: str):
        """Process skill note with proficiency tracking"""
        time.sleep(0.5)

        parsed = self.parser.parse_file(filepath)
        if not parsed:
            return

        metadata = parsed.get("metadata", {})
        proficiency = metadata.get("proficiency", 0)

        # Enhanced content with proficiency context
        enhanced = f"Skill: {parsed['filename']}\n"
        enhanced += f"Proficiency: {proficiency}/10\n"
        enhanced += f"Category: {metadata.get('category', 'general')}\n"
        enhanced += f"Last practiced: {metadata.get('last-practiced', 'unknown')}\n\n"
        enhanced += parsed["content"]

        doc_id = f"skill_{parsed['filename'].replace('.md', '')}"

        self.kb.collection.upsert(
            documents=[enhanced],
            ids=[doc_id],
            metadatas=[
                {
                    "source": parsed["filename"],
                    "type": "skill_note",
                    "proficiency": int(proficiency) if proficiency else 0,
                    "category": ", ".join(metadata.get("category", []))
                    if isinstance(metadata.get("category"), list)
                    else str(metadata.get("category", ""))
                    if isinstance(metadata.get("category"), list)
                    else str(metadata.get("category", "")),
                    "tags": ", ".join(parsed["tags"]) if parsed["tags"] else "",
                }
            ],
        )

        print(f"   ✓ Skill tracked: {proficiency}/10 proficiency")
