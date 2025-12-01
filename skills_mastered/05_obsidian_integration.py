"""
SKILL MASTERED: Obsidian Integration with Multi-Handler Watchdog
Week 2 Day 8

What I learned:
- YAML frontmatter parsing (python-frontmatter)
- Regular expressions for wikilink extraction
- Multiple event handlers per application (Observer pattern)
- Metadata-driven document classification
- Knowledge graph foundations (wikilinks = edges)

Portfolio highlight:
"Built intelligent Obsidian vault sync - automatically tracks learning from daily notes,
indexes research, and monitors skill proficiency changes in real-time using specialized
handlers per note type."

Business value:
- Zero-friction knowledge capture (write notes → auto-indexed)
- Learning analytics (skills practiced, proficiency trends)
- Searchable second brain (semantic search over all notes)

Technical complexity:
- 3 specialized handlers (DailyNote, Research, Skill)
- YAML schema validation
- Wikilink graph extraction
- Type-aware document processing
"""

import frontmatter


def demo():
    """Quick frontmatter parsing demo"""
    test_md = """---
date: 2025-12-01
skills: [python, yaml]
---
# Test Note
Content here
"""
    post = frontmatter.loads(test_md)
    print(f"Metadata: {post.metadata}")
    print(f"Content: {post.content}")


if __name__ == "__main__":
    demo()
