"""
Markdown Parser - Extract frontmatter and content
Week 2 Day 8 - YAML frontmatter + Obsidian support
"""

import frontmatter
import os
from typing import Dict, List, Optional


class MarkdownParser:
    def __init__(self):
        print("📄 Markdown Parser initialized")

    def parse_file(self, filepath: str) -> Optional[Dict]:
        """Parse markdown file with frontmatter"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)

            # Extract components
            metadata = dict(post.metadata) if post.metadata else {}
            content = post.content
            filename = os.path.basename(filepath)

            # Parse wikilinks [[Link]]
            wikilinks = self._extract_wikilinks(content)

            # Parse tags (from frontmatter or inline #tags)
            tags = self._extract_tags(metadata, content)

            return {
                "filename": filename,
                "filepath": filepath,
                "metadata": metadata,
                "content": content,
                "wikilinks": wikilinks,
                "tags": tags,
                "has_frontmatter": len(metadata) > 0,
                "word_count": len(content.split()),
            }

        except Exception as e:
            print(f"⚠️ Parse error for {filepath}: {e}")
            return None

    def _extract_wikilinks(self, content: str) -> List[str]:
        """Extract [[wikilinks]] from content"""
        import re

        pattern = r"\[\[([^\]]+)\]\]"
        links = re.findall(pattern, content)
        return links

    def _extract_tags(self, metadata: Dict, content: str) -> List[str]:
        """Extract tags from frontmatter and inline #tags"""
        tags = []

        # From frontmatter
        if "tags" in metadata:
            fm_tags = metadata["tags"]
            if isinstance(fm_tags, list):
                tags.extend(fm_tags)
            elif isinstance(fm_tags, str):
                tags.append(fm_tags)

        # From inline #tags
        import re

        inline_tags = re.findall(r"#(\w+)", content)
        tags.extend(inline_tags)

        return list(set(tags))  # Remove duplicates

    def extract_skills(self, parsed_data: Dict) -> List[str]:
        """Extract skills from metadata or content"""
        skills = []

        # From frontmatter 'skills' field
        metadata = parsed_data.get("metadata", {})
        if "skills" in metadata:
            fm_skills = metadata["skills"]
            if isinstance(fm_skills, list):
                skills.extend(fm_skills)

        # From tags that look like skills
        tags = parsed_data.get("tags", [])
        skill_tags = [
            t
            for t in tags
            if any(
                keyword in t.lower()
                for keyword in ["python", "pandas", "sql", "git", "api"]
            )
        ]
        skills.extend(skill_tags)

        return list(set(skills))

    def classify_note_type(self, parsed_data: Dict) -> str:
        """Classify note based on frontmatter and tags"""
        metadata = parsed_data.get("metadata", {})
        tags = parsed_data.get("tags", [])
        filepath = parsed_data.get("filepath", "")

        # By folder
        if "/daily/" in filepath:
            return "daily_note"
        elif "/research/" in filepath:
            return "research"
        elif "/skills/" in filepath:
            return "skill_note"
        elif "/goals/" in filepath:
            return "goal"
        elif "/projects/" in filepath:
            return "project"

        # By tags
        if "daily" in tags:
            return "daily_note"
        elif "research" in tags:
            return "research"
        elif "skill" in tags:
            return "skill_note"

        return "general"


# Quick test
if __name__ == "__main__":
    parser = MarkdownParser()

    # Test with a sample file
    test_file = """---
date: 2025-12-01
tags: [daily, learning, python]
skills: [watchdog, yaml]
progress: completed
---

# Today's Learning

Learned [[Skills/Python]] and [[Skills/YAML]] parsing.
Built advanced file monitoring with #obsidian integration.

## Skills Practiced
- File I/O
- YAML frontmatter
"""

    # Save test file
    os.makedirs("data/test", exist_ok=True)
    with open("data/test/test_note.md", "w") as f:
        f.write(test_file)

    print("\n--- Testing Markdown Parser ---")
    parsed = parser.parse_file("data/test/test_note.md")

    if parsed:
        print(f"\n✅ Parsed: {parsed['filename']}")
        print(f"   Frontmatter: {parsed['has_frontmatter']}")
        print(f"   Metadata: {parsed['metadata']}")
        print(f"   Wikilinks: {parsed['wikilinks']}")
        print(f"   Tags: {parsed['tags']}")
        print(f"   Skills: {parser.extract_skills(parsed)}")
        print(f"   Type: {parser.classify_note_type(parsed)}")
        print(f"   Content preview: {parsed['content'][:100]}...")
