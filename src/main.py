"""
AI Career Coach - Week 1 Day 3
Now with personal knowledge base (RAG)!
"""

import os
import sys
from datetime import datetime
from llm_engine import LocalLLM
from rag_engine import KnowledgeBase
from file_watcher import FileWatcher


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

        # Optinal file watcher
        self.watcher = None
        if enable_watcher:
            watch_folders = [
                "data/monitored_folders/job_posts",
                "data/knowledge_base/skills",
            ]
            self.watcher = FileWatcher(watch_folders)

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


def main():
    print("=" * 70)
    print("🚀 AI CAREER COACH - Week 1 Day 5")
    print("   Real-Time File Monitoring!")
    print("=" * 70)

    # Check command line args
    if len(sys.argv) > 1 and sys.argv[1] == "--watch":
        # Monitor mode
        coach = CareerCoach(enable_watcher=True)
        coach.load_knowledge()

        print("\n" + "=" * 70)
        print("Entering WATCH MODE")
        print("Drop files into monitored folders for instant analysis!")
        print("=" * 70)

        try:
            coach.start_monitoring()
            import time

            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            coach.stop_monitoring()
            print("\n👋 Goodbye!")

    else:
        # Standard mode
        coach = CareerCoach(enable_watcher=False)
        coach.load_knowledge()

    # Test RAG-powered conversation
    print("\n" + "=" * 70)
    print("--- Job Fit Analysis ---")

    coach.analyze_job_fit("python_finance_analyst")

    print("\n" + "=" * 70)
    print("✅ DAY 5 COMPLETE!")
    print("📝 Next: Day 6-7 - Week 1 wrap-up + demo video")
    print("🔥 Streak: 5/56 days")
    print("🍕 Reward: 2 more days → Pizza delivery!")
    print("\n💡 TIP: Run with --watch to enable file monitoring:")
    print("   python src/main.py --watch")
    print("=" * 70)


if __name__ == "__main__":
    main()
