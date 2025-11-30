"""
SKILL MASTERED: Local LLM Integration with Ollama
Week 1 Day 2

What I learned:
- Connecting to local LLM via Ollama API
- System prompts for consistent AI personality
- Context injection for personalized responses
- Error handling for service connectivity

Portfolio highlight:
"Built AI career coach using local LLM (privacy-first, no cloud dependency)"
"""

import ollama


def demo():
    """Quick demo of local LLM skill"""
    response = ollama.generate(
        model="llama3.2",
        prompt="Give career advice for economist learning Python in 1 sentence.",
        options={"temperature": 0.7},
    )
    print(response["response"])


if __name__ == "__main__":
    demo()
