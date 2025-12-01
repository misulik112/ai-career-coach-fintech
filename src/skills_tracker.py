"""
Skills Proficiency Tracker
Week 2 Day 9 - Extract and track skill levels from metadata
"""

from rag_engine import KnowledgeBase
from markdown_parser import MarkdownParser
from datetime import datetime
from typing import Dict, List, Optional
import json
import os


class SkillsTracker:
    """Track skill proficiency over time"""

    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        self.parser = MarkdownParser()
        self.history_file = "data/skills_history.json"
        self.load_history()
        print("📊 Skills Tracker initialized")

    def load_history(self):
        """Load historical skill data"""
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                self.history = json.load(f)
        else:
            self.history = {}

    def save_history(self):
        """Save skill history to file"""
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, "w") as f:
            json.dump(self.history, indent=2, fp=f)

    def extract_all_skills(self) -> Dict[str, Dict]:
        """Extract all skills from knowledge base"""
        # Query for skill notes
        results = self.kb.collection.get(where={"type": "skill_note"})

        skills = {}

        if results and results["ids"]:
            for i, doc_id in enumerate(results["ids"]):
                metadata = results["metadatas"][i]

                skill_name = metadata.get("source", doc_id).replace(".md", "")
                proficiency = metadata.get("proficiency", 0)

                skills[skill_name] = {
                    "proficiency": proficiency,
                    "category": metadata.get("category", "general"),
                    "tags": metadata.get("tags", []),
                    "last_updated": datetime.now().isoformat(),
                }

        return skills

    def extract_practiced_skills(self, days: int = 7) -> List[str]:
        """Extract skills practiced in last N days from daily notes"""
        results = self.kb.collection.get(where={"type": "daily_note"})

        practiced = []

        if results and results["metadatas"]:
            for metadata in results["metadatas"]:
                skills = metadata.get("skills", [])
                if isinstance(skills, list):
                    practiced.extend(skills)
                elif isinstance(skills, str):
                    # Handle string format
                    practiced.append(skills)

        # Remove duplicates, maintain frequency
        from collections import Counter

        skill_counts = Counter(practiced)

        return skill_counts

    def update_skill_history(self, skill_name: str, proficiency: int):
        """Record proficiency change"""
        if skill_name not in self.history:
            self.history[skill_name] = []

        entry = {"date": datetime.now().isoformat(), "proficiency": proficiency}

        self.history[skill_name].append(entry)
        self.save_history()

    def get_skill_progress(self, skill_name: str) -> Optional[Dict]:
        """Get progress for specific skill"""
        if skill_name not in self.history or len(self.history[skill_name]) < 2:
            return None

        records = self.history[skill_name]
        first = records[0]
        last = records[-1]

        return {
            "skill": skill_name,
            "start_level": first["proficiency"],
            "current_level": last["proficiency"],
            "improvement": last["proficiency"] - first["proficiency"],
            "start_date": first["date"],
            "last_updated": last["date"],
            "total_updates": len(records),
        }

    def generate_progress_report(self) -> str:
        """Generate weekly progress summary"""
        skills = self.extract_all_skills()
        practiced = self.extract_practiced_skills(days=7)

        report = "📊 WEEKLY SKILLS REPORT\n"
        report += "=" * 60 + "\n\n"

        # Current skills
        report += "📚 Current Skills Inventory:\n"
        for skill, data in sorted(
            skills.items(), key=lambda x: x[1]["proficiency"], reverse=True
        ):
            proficiency = data["proficiency"]
            bar = "█" * proficiency + "░" * (10 - proficiency)
            report += f"  {skill:<20} [{bar}] {proficiency}/10\n"

        report += f"\n📈 Most Practiced (Last 7 Days):\n"
        for skill, count in practiced.most_common(5):
            report += f"  {skill:<20} ({count} mentions)\n"

        # Progress tracking
        report += f"\n🚀 Progress This Week:\n"
        improvements = []
        for skill_name in skills.keys():
            progress = self.get_skill_progress(skill_name)
            if progress and progress["improvement"] > 0:
                improvements.append(progress)

        if improvements:
            for prog in sorted(
                improvements, key=lambda x: x["improvement"], reverse=True
            ):
                report += f"  {prog['skill']:<20} {prog['start_level']}→{prog['current_level']} (+{prog['improvement']})\n"
        else:
            report += "  No proficiency updates yet. Update your skill notes!\n"

        report += "\n" + "=" * 60

        return report

    def compare_with_job_requirements(self, job_skills: List[str]) -> Dict:
        """Compare current skills against job requirements"""
        current_skills = self.extract_all_skills()

        matches = []
        gaps = []

        for required_skill in job_skills:
            # Fuzzy match (lowercase, partial)
            found = False
            for current_skill, data in current_skills.items():
                if required_skill.lower() in current_skill.lower():
                    matches.append(
                        {
                            "skill": required_skill,
                            "proficiency": data["proficiency"],
                            "status": "match",
                        }
                    )
                    found = True
                    break

            if not found:
                gaps.append(
                    {"skill": required_skill, "proficiency": 0, "status": "gap"}
                )

        # Calculate readiness
        total_required = len(job_skills)
        total_proficiency = sum(m["proficiency"] for m in matches)
        max_possible = total_required * 10

        readiness = (total_proficiency / max_possible * 100) if max_possible > 0 else 0

        return {
            "matches": matches,
            "gaps": gaps,
            "readiness_score": round(readiness, 1),
            "skills_matched": len(matches),
            "total_required": total_required,
        }


# Quick test
if __name__ == "__main__":
    kb = KnowledgeBase()
    tracker = SkillsTracker(kb)

    print("\n" + tracker.generate_progress_report())

    print("\n--- Testing Job Comparison ---")
    job_reqs = ["Python", "Pandas", "SQL", "Git"]
    comparison = tracker.compare_with_job_requirements(job_reqs)

    print(f"\n🎯 Job Readiness: {comparison['readiness_score']}%")
    print(
        f"   Skills matched: {comparison['skills_matched']}/{comparison['total_required']}"
    )

    if comparison["gaps"]:
        print(f"\n❌ Missing skills:")
        for gap in comparison["gaps"]:
            print(f"   - {gap['skill']}")
