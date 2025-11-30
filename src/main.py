"""
AI Career Coach - Week 1 Day 2
Now with REAL local LLM intelligence!
"""

import os
from datetime import datetime
from llm_engine import LocalLLM


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

        print("🤖 AI Career Coach initialized!")
        print(f"👤 Profile: {self.user_profile['current_role']}")
        print(f"🎯 Goal: {self.user_profile['target_role']}")
        print(f"⏱️  Timeline: {self.user_profile['transition_timeline']}")
        print(f"🧠 Brain: Local LLM (Ollama llama3.2)")

    def chat(self, message):
        """Chat with AI coach using local LLM"""
        self.user_profile["session_count"] += 1

        print(f"\n💬 You: {message}")

        # Add user context to help LLM
        context = f"Session #{self.user_profile['session_count']}"

        # Get response from local LLM
        response = self.llm.chat(message, context=context)

        print(f"🤖 Coach: {response}")
        return response

    def get_stats(self):
        """Show session statistics"""
        print(f"\n📊 Session Stats:")
        print(f"   Total conversations: {self.user_profile['session_count']}")
        print(f"   Started: {self.user_profile['first_session']}")


def main():
    print("=" * 60)
    print("🚀 AI CAREER COACH - Week 1 Day 2")
    print("   Real Local LLM intelligence")
    print("=" * 60)

    # Initialize coach
    coach = CareerCoach()

    # Test conversation flow
    print("\n--- Testing Real AI Conversation ---")

    coach.chat("Hello! I'm excited to start my transition.")

    coach.chat("What's the first Python skill I should learn as an economist?")

    coach.chat("How can I use my econometrics background?")

    # Show Stats
    coach.get_stats()

    print("\n" + "=" * 60)
    print("✅ DAY 2 COMPLETE!")
    print("📝 Next: Day 3 - Add Chroma vector DB for CV analysis")
    print("🔥 Streak: 2/56 days")
    print("🎮 Reward progress: 1 more day → Gaming unlocked!")
    print("=" * 60)


if __name__ == "__main__":
    main()
