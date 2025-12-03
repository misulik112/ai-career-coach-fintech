"""
Local LLM Engine using Ollama
Week 1 Day 2 - My economist -< freelancer brain
"""

import ollama
from config import Config


class LocalLLM:
    def __init__(self, model="llama3.2"):
        # Use config instead of hardcoded values
        self.model = Config.OLLAMA_MODEL
        self.host = Config.OLLAMA_HOST
        self.temperature = Config.LLM_TEMPERATURE
        self.max_tokens = Config.LLM_MAX_TOKENS

        self.system_prompt = """You are an AI Career Coach specializing in helping 
        economists transition to Python programming careers in finance.

My user profile:
- Current: Economist with 8 years experience working for a multinational company
- Goal: Become Python finance freelancer earning €1500/month
- Timeline: 12 months
- Strengths: Economic modeling, statistical analysis, time series

Your role:
- Give actionable, specific advice
- Connect my econ skills to Python/finance opportunities
- Be supportive but direct
- Keep responses under 100 words unless asked for details"""

        print(f"🧠 Local LLM initialized: {self.model}")
        print(f"   Host: {self.host}")
        print(f"   Temperature: {self.temperature}")

    def chat(self, user_message, context=None):
        """Send message to local LLM and get response"""

        # Build full prompt with context
        if context:
            full_prompt = f"{self.system_prompt}\n\nContext: {context}\n\nUser: {user_message}\n\nCoach:"
        else:
            full_prompt = f"{self.system_prompt}\n\nUser: {user_message}\n\nCoach:"

        try:
            # Call Ollama
            response = ollama.generate(
                model=self.model,
                prompt=full_prompt,
                options={
                    "temperature": 0.7,  # Balanced creativity
                    "num_predict": 200,  # Max tokens
                },
            )

            return response["response"].strip()

        except Exception as e:
            return f"⚠️ LLM Error: {e}\n\nTip: Is Ollama running? Try: ollama serve"


# Quick test
if __name__ == "__main__":
    llm = LocalLLM()

    print("-n--- Testing Local LLM ---")
    response = llm.chat("Hello! I'm an economist wanting to learn Python for finance.")
    print(f"\n🤖 Coach: {response}\n")
