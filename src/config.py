"""
Configuration Management with Environment Variables
Week 3 Day 15 - Professional config handling
"""

import os
from pathlib import Path
from typing import Optional, List
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Config:
    """Central configuration from environment variables"""

    # =============================================================================
    # LLM Configuration
    # =============================================================================
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "500"))

    # =============================================================================
    # API Keys (Optional)
    # =============================================================================
    ANYTYPE_API_KEY: Optional[str] = os.getenv("ANYTYPE_API_KEY")
    ANYTYPE_SPACE_ID: Optional[str] = os.getenv("ANYTYPE_SPACE_ID")

    PERPLEXITY_API_KEY: Optional[str] = os.getenv("PERPLEXITY_API_KEY")

    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")

    # =============================================================================
    # Paths
    # =============================================================================
    BASE_DIR: Path = Path(__file__).parent.parent
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "data/vector_db")
    KNOWLEDGE_BASE_PATH: str = os.getenv("KNOWLEDGE_BASE_PATH", "data/knowledge_base")
    OBSIDIAN_VAULT_PATH: str = os.getenv("OBSIDIAN_VAULT_PATH", "data/obsidian_vault")
    ANYTYPE_CACHE_PATH: str = os.getenv("ANYTYPE_CACHE_PATH", "data/anytype_cache")
    CACHE_DIR: str = os.getenv("CACHE_DIR", "data/cache")

    # =============================================================================
    # Cache Configuration
    # =============================================================================
    CACHE_TTL_DAYS: int = int(os.getenv("CACHE_TTL_DAYS", "90"))

    # =============================================================================
    # Feature Flags
    # =============================================================================
    ENABLE_OBSIDIAN_WATCHER: bool = (
        os.getenv("ENABLE_OBSIDIAN_WATCHER", "false").lower() == "true"
    )
    ENABLE_ANYTYPE_SYNC: bool = (
        os.getenv("ENABLE_ANYTYPE_SYNC", "false").lower() == "true"
    )
    ENABLE_CACHE: bool = os.getenv("ENABLE_CACHE", "true").lower() == "true"

    # =============================================================================
    # Logging
    # =============================================================================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/coach.log")

    # =============================================================================
    # OCR Configuration
    # =============================================================================
    TESSDATA_PREFIX: Optional[str] = os.getenv("TESSDATA_PREFIX")
    OCR_DEFAULT_LANGUAGE: str = os.getenv("OCR_DEFAULT_LANGUAGE", "eng")
    OCR_AUTO_DETECT: bool = os.getenv("OCR_AUTO_DETECT", "false").lower() == "true"
    OCR_LANGUAGES: List[str] = os.getenv("OCR_LANGUAGES", "eng").split(",")

    # Set TESSDATA_PREFIX if configured
    if TESSDATA_PREFIX and os.path.exists(TESSDATA_PREFIX):
        import os as _os

        _os.environ["TESSDATA_PREFIX"] = TESSDATA_PREFIX

    @classmethod
    def validate(cls):
        """Validate configuration and show warnings"""
        issues = []

        # Check if .env exists
        if not env_path.exists():
            issues.append("⚠️  .env file not found. Copy .env.example to .env")

        # Check Ollama
        if cls.OLLAMA_HOST == "http://localhost:11434":
            issues.append("ℹ️  Using default Ollama host (localhost:11434)")

        # Check API keys
        if not cls.ANYTYPE_API_KEY and cls.ENABLE_ANYTYPE_SYNC:
            issues.append("⚠️  Anytype sync enabled but no API key set")

        if not cls.PERPLEXITY_API_KEY:
            issues.append("ℹ️  Perplexity API key not set (web research disabled)")

        if not cls.OPENAI_API_KEY:
            issues.append("ℹ️  OpenAI API key not set (using Ollama only)")

        return issues

    @classmethod
    def print_config(cls):
        """Print current configuration (safely)"""
        print("\n🔧 Configuration:")
        print("=" * 70)

        # LLM
        print(f"📡 LLM:")
        print(f"   Host: {cls.OLLAMA_HOST}")
        print(f"   Model: {cls.OLLAMA_MODEL}")
        print(f"   Temperature: {cls.LLM_TEMPERATURE}")

        # API Keys (masked)
        print(f"\n🔑 API Keys:")
        print(f"   Anytype: {'✅ Set' if cls.ANYTYPE_API_KEY else '❌ Not set'}")
        print(f"   Perplexity: {'✅ Set' if cls.PERPLEXITY_API_KEY else '❌ Not set'}")
        print(f"   OpenAI: {'✅ Set' if cls.OPENAI_API_KEY else '❌ Not set'}")

        # Paths
        print(f"\n📁 Paths:")
        print(f"   Knowledge base: {cls.KNOWLEDGE_BASE_PATH}")
        print(f"   Vector DB: {cls.CHROMA_DB_PATH}")
        print(f"   Cache: {cls.CACHE_DIR}")

        # Features
        print(f"\n⚡ Features:")
        print(f"   Obsidian watcher: {'✅' if cls.ENABLE_OBSIDIAN_WATCHER else '❌'}")
        print(f"   Anytype sync: {'✅' if cls.ENABLE_ANYTYPE_SYNC else '❌'}")
        print(f"   Cache: {'✅' if cls.ENABLE_CACHE else '❌'}")

        print("=" * 70)

        # Validation warnings
        issues = cls.validate()
        if issues:
            print("\n⚠️  Configuration Issues:")
            for issue in issues:
                print(f"   {issue}")
            print()

    @classmethod
    def get_api_key(cls, service: str) -> Optional[str]:
        """Safely get API key for a service"""
        keys = {
            "anytype": cls.ANYTYPE_API_KEY,
            "perplexity": cls.PERPLEXITY_API_KEY,
            "openai": cls.OPENAI_API_KEY,
        }
        return keys.get(service.lower())


# Test config on import
if __name__ == "__main__":
    print("=" * 70)
    print("🔧 CONFIGURATION TEST")
    print("=" * 70)

    Config.print_config()

    print("\n--- Testing API Key Access ---")
    print(f"Anytype key available: {Config.get_api_key('anytype') is not None}")
    print(f"Perplexity key available: {Config.get_api_key('perplexity') is not None}")
    print(f"OpenAI key available: {Config.get_api_key('openai') is not None}")

    print("\n" + "=" * 70)
    print("✅ Configuration loaded successfully!")
    print("=" * 70)
