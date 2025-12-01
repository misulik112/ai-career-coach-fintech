"""
AI Career Coach - Week 1 Day 3
Now with personal knowledge base (RAG)!
"""

import os
import sys
from datetime import datetime
from typing import List
from llm_engine import LocalLLM
from rag_engine import KnowledgeBase
from file_watcher import FileWatcher
from skills_tracker import SkillsTracker
from knowledge_graph import KnowledgeGraph


class CareerCoach:
    def __init__(self, enable_watcher=False):
        self.user_profile = {
            "current_role": "Economist (8 years)",
            "target_role": "Python Finance Freelancer",
            "transition_timeline": "12 months",
            "session_count": 0,
            "first_session": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

        # Initialize local LLM
        self.llm = LocalLLM()

        # Initialize rag engine
        self.kb = KnowledgeBase()

        # Optional file watcher
        self.watcher = None
        if enable_watcher:
            watch_folders = [
                "data/monitored_folders/job_posts",
                "data/knowledge_base/skills",
            ]
            self.watcher = FileWatcher(watch_folders)

        # Skills tracker
        self.skills_tracker = SkillsTracker(self.kb)

        # Initialize the knowledge_graph
        self.knowledge_graph = None

        print("🤖 AI Career Coach initialized!")
        print(f"👤 Profile: {self.user_profile['current_role']}")
        print(f"🎯 Goal: {self.user_profile['target_role']}")
        print(f"🧠 Brain: Local LLM + RAG Knowledge Base)")
        if enable_watcher:
            print(f"👁️  File Watcher: ENABLED")

    def start_monitoring(self):
        """Start real-time file monitoring"""
        if self.watcher:
            print("\n🔍 Starting file monitoring...")
            self.watcher.start()
        else:
            print("⚠️ File watcher not enabled")

    def stop_monitoring(self):
        """Stop file monitoring"""
        if self.watcher:
            self.watcher.stop()

    def load_knowledge(self):
        """Load personal knowledge into vector DB"""
        print("\n📚 Loading your skills and goals...")
        self.kb.load_knowledge_files()
        self.kb.load_job_posts()

    def chat(self, message):
        """Chat with AI coach using local LLM"""
        self.user_profile["session_count"] += 1

        print(f"\n💬 You: {message}")

        # Search knowledge base for relevant context
        relevant_context = self.kb.search(message, n_results=2)

        # Get response from LLM with retrieved context
        response = self.llm.chat(message, context=relevant_context)

        print(f"🤖 Coach: {response}")
        return response

    def analyze_skills_gap(self):
        """Special analysis: What skills to learn?"""
        print("\n🔍 Running Skills Gap Analysis...")
        query = "Compare my current economics and Python skills to my transition goals."
        context = self.kb.search(query, n_results=3)
        prompt = "Based on my current skills and goals, what are the top 3 Python skills I should focus on this month? Be specific."
        response = self.llm.chat(prompt, context=context)

        print(f"🤖 Coach Analysis:\n{response}")

    def show_skills_report(self):
        """Display weekly skills progress"""
        print("\n" + self.skills_tracker.generate_progress_report())

    def analyze_job_readiness(self, job_skills: List[str]):
        """Analyze readiness for job based on skills"""
        print(f"\n🎯 JOB READINESS ANALYSIS")
        print("=" * 60)

        comparison = self.skills_tracker.compare_with_job_requirements(job_skills)

        # Display results
        print(f"\n📊 Readiness Score: {comparison['readiness_score']}%")
        print(
            f"   Skills Matched: {comparison['skills_matched']}/{comparison['total_required']}"
        )

        if comparison["matches"]:
            print(f"\n✅ Skills You Have:")
            for match in sorted(
                comparison["matches"], key=lambda x: x["proficiency"], reverse=True
            ):
                bar = "█" * match["proficiency"] + "░" * (10 - match["proficiency"])
                print(f"   {match['skill']:<15} [{bar}] {match['proficiency']}/10")

        if comparison["gaps"]:
            print(f"\n❌ Skills to Learn:")
            for gap in comparison["gaps"]:
                print(f"   - {gap['skill']}")

            # Get LLM recommendation
            gaps_list = [g["skill"] for g in comparison["gaps"]]
            prompt = f"I need to learn these skills: {', '.join(gaps_list)}. Give me a 2-week action plan (3 bullet points max)."

            context = f"Current skills: {[m['skill'] for m in comparison['matches']]}"
            recommendation = self.llm.chat(prompt, context=context)

            print(f"\n🤖 Coach Recommendation:")
            print(f"   {recommendation}")

        print("=" * 60)

    def get_stats(self):
        """Show session statistics"""
        print(f"\n📊 Session Stats:")
        print(f"   Total conversations: {self.user_profile['session_count']}")
        print(f"   Started: {self.user_profile['first_session']}")

    def analyze_job_fit(self, job_name="python_finance_analyst"):
        """Analyze fit for a specific job"""
        print(f"\n🎯 Analyzing Job Fit: {job_name}")
        print("=" * 60)

        # Get job requirements
        job_query = f"job_{job_name} requirements skills responsibilities"
        job_context = self.kb.search(job_query, n_results=1)

        # Get your skills
        skills_query = "my economics expertise python skills current level"
        skills_context = self.kb.search(skills_query, n_results=2)

        # Combined context
        full_context = (
            f"JOB REQUIREMENTS:\n{job_context}\n\nMY CURRENT SKILLS:\n{skills_context}"
        )

        # Ask LLM for analysis
        prompt = """Analyze this job posting against my skills:

1. What skills do I already have that match? (be specific)
2. What are my top 3 skill gaps?
3. What's my estimated readiness? (0-100%)
4. What should I learn THIS WEEK to improve fit?

Be direct and actionable."""

        response = self.llm.chat(prompt, context=full_context)

        print(f"\n🤖 Coach Analysis:\n{response}")
        print("=" * 60)

    def build_knowledge_graph(self, vault_path="data/obsidian_vault"):
        """Build knowledge graph from Obsidian vault"""
        print("\n🕸️  Building knowledge graph...")
        self.knowledge_graph = KnowledgeGraph(self.kb)
        self.knowledge_graph.build_from_vault(vault_path)
        return self.knowledge_graph

    def show_learning_path(self, from_skill: str, to_goal: str):
        """Show how a skill connects to a goal"""
        if not self.knowledge_graph:
            print("⚠️ Build knowledge graph first!")
            return

        print(f"\n🎯 LEARNING PATH ANALYSIS")
        print("=" * 60)
        print(f"From: {from_skill}")
        print(f"To:   {to_goal}")

        path = self.knowledge_graph.find_path(from_skill, to_goal)

        if path:
            print(f"\n✅ Path found ({len(path) - 1} steps):\n")
            for i, node in enumerate(path):
                indent = "   " * i
                arrow = "→" if i < len(path) - 1 else "★"
                node_type = self.knowledge_graph.nodes.get(node, {}).get(
                    "type", "unknown"
                )
                print(f"{indent}{arrow} {node} ({node_type})")

            # Get LLM insight
            path_str = " → ".join(path)
            prompt = f"I want to go from {from_skill} to {to_goal}. The connection path is: {path_str}. Give me 3 actionable steps (brief)."

            insight = self.llm.chat(prompt, context="")
            print(f"\n🤖 Coach Recommendation:")
            print(f"   {insight}")
        else:
            print("\n❌ No direct path found")
            print("   Try creating a note that links these concepts!")

        print("=" * 60)

    def explore_connections(self, node_name: str):
        """Explore all connections for a concept"""
        if not self.knowledge_graph:
            print("⚠️ Build knowledge graph first!")
            return

        self.knowledge_graph.visualize_connections(node_name, max_depth=2)


def main():
    print("=" * 70)
    print("🚀 AI CAREER COACH - Week 2 Day 10")
    print("   Knowledge Graph & Learning Paths!")
    print("=" * 70)

    # Initialize coach
    coach = CareerCoach(enable_watcher=False)
    coach.load_knowledge()

    # Build knowledge graph
    graph = coach.build_knowledge_graph()

    print("\n" + "=" * 70)
    print("--- Graph Statistics ---")
    stats = graph.get_node_stats()
    print(f"📊 Total concepts tracked: {stats['total_nodes']}")
    print(f"🔗 Total connections: {stats['total_edges']}")

    if stats["top_connected"]:
        print(f"\n🏆 Your most central concepts:")
        for node, count in stats["top_connected"][:3]:
            print(f"   • {node}: {count} connections")

    print("\n" + "=" * 70)
    print("--- Connection Explorer ---")
    coach.explore_connections("skills/Python")

    print("\n" + "=" * 70)
    print("--- Learning Path ---")
    coach.show_learning_path("skills/Python", "goals/Freelance Transition")

    print("\n" + "=" * 70)
    print("✅ DAY 10 COMPLETE!")
    print("📝 Next: Day 11 - Smart document chunking")
    print("🔥 Streak: 10/56 days 🎉 DOUBLE DIGITS!")
    print("🎧 Reward: 4 more days → Audiobook!")
    print("=" * 70)


if __name__ == "__main__":
    main()
