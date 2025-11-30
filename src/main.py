"""
AI Career Coach - Week 1 Day 3
Now with personal knowledge base (RAG)!
"""

import os
from datetime import datetime
from llm_engine import LocalLLM
from rag_engine import KnowledgeBase


class CareerCoach:
    def __init__(self):
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

        print("🤖 AI Career Coach initialized!")
        print(f"👤 Profile: {self.user_profile['current_role']}")
        print(f"🎯 Goal: {self.user_profile['target_role']}")
        print(f"🧠 Brain: Local LLM + RAG Knowledge Base)")

    def load_knowledge(self):
        """Load personal knowledge into vector DB"""
        print("\n📚 Loading your skills and goals...")
        self.kb.load_knowledge_files()

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


def main():
    print("=" * 70)
    print("🚀 AI CAREER COACH - Week 1 Day 3")
    print("   Personal Knowledge Base (RAG) Online!")
    print("=" * 70)

    # Initialize coach
    coach = CareerCoach()

    # Load knowledge
    coach.load_knowledge()

    # Test RAG-powered conversation
    print("\n--- Testing RAG-Powered Conversation ---")

    coach.chat("What econometric methods do I already know?.")

    coach.chat("How can I use my Excel skills in Python?")

    # Show Stats
    coach.get_stats()

    print("\n" + "=" * 70)
    print("✅ DAY 3 COMPLETE!")
    print("📝 Next: Day 4 - PDF file loader for job descriptions")
    print("🔥 Streak: 3/56 days")
    print("🎮 REWARD UNLOCKED: 1 hour gaming time!")
    print("=" * 70)


if __name__ == "__main__":
    main()
