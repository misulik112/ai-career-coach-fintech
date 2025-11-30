"""
AI Career Coach - Week 1 Day 1
My personal economist -> FinTech Python freelancer transition system
"""

import os
from datetime import datetime


class CareerCoach:
    def __init__(self):
        self.user_profile = {
            "current_role": "Economist (8 years)",
            "target_role": "Python Finance Freelancer",
            "transition_timeline": "12 months",
            "first_session": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        print("🤖 AI Career Coach initialized!")
        print(f"👤 Profile: {self.user_profile['current_role']}")
        print(f"🎯 Goal: {self.user_profile['target_role']}")
        print(f"⏱️  Timeline: {self.user_profile['transition_timeline']}")

    def chat(self, message):
        """Simple echo for Day 1 - we'll add LLM next"""
        print(f"\n💬 You: {message}")

        # Basic responses
        if "hello" in message.lower():
            response = f"Hello! Ready to transition from economist to Python freelancer? Let's build your future together!"
        elif "skills" in message.lower():
            response = "Great question! Tomorrow we'll load your CV and analyze your economist skills vs Python finance requirements."
        else:
            response = f"I heard: '{message}'. By Week 8, I'll give you personalized career advice using local LLM + Perplexity research!"

        print(f"🤖 Coach: {response}")
        return response


def main():
    print("=" * 60)
    print("🚀 AI CAREER COACH - Week 1 Day 1")
    print("=" * 60)

    # Initialize coach
    coach = CareerCoach()

    # Test conversation
    print("\n--- Testing Basic Chat ---")
    coach.chat("Hello!")
    coach.chat("What skills should I learn?")
    coach.chat("I'm excited to start coding!")

    print("\n" + "=" * 60)
    print("✅ DAY 1 COMPLETE!")
    print("📝 Next: Day 2 - Connect Ollama local LLM")
    print("☕ Reward unlocked: Coffee time!")
    print("=" * 60)


if __name__ == "__main__":
    main()
