"""
Query Cache System
Week 2 Day 12 - Cache expensive queries with TTL
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path
from config import Config


class QueryCache:
    """Cache system for expensive queries (API calls, LLM responses)"""

    def __init__(self):
        self.cache_dir = Config.CACHE_DIR
        self.default_ttl_days = Config.CACHE_TTL_DAYS

        self.cache_dir = Path(self.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = timedelta(days=self.default_ttl_days)
        # Stats
        self.stats = {"hits": 0, "misses": 0, "saves": 0}

        print(f"💾 Query Cache initialized")
        print(f"   Cache dir: {self.cache_dir}")
        print(f"   Default TTL: {self.default_ttl_days} days")

    def _hash_query(self, query: str) -> str:
        """Generate hash for query (cache key)"""
        return hashlib.md5(query.lower().strip().encode()).hexdigest()

    def _cache_filepath(self, query_hash: str) -> Path:
        """Get filepath for cached query"""
        return self.cache_dir / f"{query_hash}.json"

    def get(self, query: str) -> Optional[Dict[str, Any]]:
        """Get cached result if exists and not expired"""
        query_hash = self._hash_query(query)
        cache_file = self._cache_filepath(query_hash)

        if not cache_file.exists():
            self.stats["misses"] += 1
            return None

        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cached_data = json.load(f)

            # Check expiry
            expires_at = datetime.fromisoformat(cached_data["expires_at"])

            if datetime.now() > expires_at:
                # Expired - delete cache file
                cache_file.unlink()
                self.stats["misses"] += 1
                print(f"   ⏰ Cache expired: {query[:50]}...")
                return None

            # Valid cache hit!
            self.stats["hits"] += 1
            age_hours = (
                datetime.now() - datetime.fromisoformat(cached_data["cached_at"])
            ).total_seconds() / 3600
            print(f"   ✅ Cache HIT! ({age_hours:.1f}h old)")

            return cached_data["result"]

        except Exception as e:
            print(f"   ⚠️ Cache read error: {e}")
            self.stats["misses"] += 1
            return None

    def set(
        self,
        query: str,
        result: Any,
        ttl_days: Optional[int] = None,
        metadata: Optional[Dict] = None,
    ):
        """Cache query result with TTL"""
        query_hash = self._hash_query(query)
        cache_file = self._cache_filepath(query_hash)

        ttl = timedelta(days=ttl_days) if ttl_days else self.default_ttl

        cache_data = {
            "query": query,
            "result": result,
            "cached_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + ttl).isoformat(),
            "ttl_days": ttl_days or self.default_ttl.days,
            "metadata": metadata or {},
        }

        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2)

            self.stats["saves"] += 1
            print(f"   💾 Cached: {query[:50]}... (TTL: {cache_data['ttl_days']}d)")

        except Exception as e:
            print(f"   ⚠️ Cache write error: {e}")

    def invalidate(self, query: str) -> bool:
        """Manually invalidate cached query"""
        query_hash = self._hash_query(query)
        cache_file = self._cache_filepath(query_hash)

        if cache_file.exists():
            cache_file.unlink()
            print(f"   🗑️  Cache invalidated: {query[:50]}...")
            return True
        return False

    def clear_expired(self) -> int:
        """Remove all expired cache entries"""
        expired_count = 0

        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, "r") as f:
                    data = json.load(f)

                expires_at = datetime.fromisoformat(data["expires_at"])

                if datetime.now() > expires_at:
                    cache_file.unlink()
                    expired_count += 1

            except Exception:
                pass  # Skip corrupted files

        if expired_count > 0:
            print(f"   🗑️  Cleared {expired_count} expired cache entries")

        return expired_count

    def clear_all(self) -> int:
        """Clear entire cache"""
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            count += 1

        print(f"   🗑️  Cleared {count} cache entries")
        return count

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (
            (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        )

        cache_files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files) / 1024  # KB

        return {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "saves": self.stats["saves"],
            "total_requests": total_requests,
            "hit_rate": round(hit_rate, 1),
            "cached_entries": len(cache_files),
            "cache_size_kb": round(total_size, 2),
        }

    def print_stats(self):
        """Print cache statistics"""
        stats = self.get_stats()

        print(f"\n📊 Cache Statistics:")
        print(f"   Hits: {stats['hits']}")
        print(f"   Misses: {stats['misses']}")
        print(f"   Hit rate: {stats['hit_rate']}%")
        print(f"   Cached entries: {stats['cached_entries']}")
        print(f"   Cache size: {stats['cache_size_kb']} KB")


# Quick test
if __name__ == "__main__":
    cache = QueryCache()

    print("\n" + "=" * 60)
    print("Testing Query Cache")
    print("=" * 60)

    # Test 1: Cache miss
    print("\n--- Test 1: First query (cache miss) ---")
    query = "What are Python finance salaries in Europe?"
    result = cache.get(query)
    print(f"Result: {result}")

    # Save to cache
    print("\n--- Saving to cache ---")
    cache.set(
        query,
        {
            "answer": "€65-95k for mid-level Python finance roles",
            "source": "market_research",
            "date": "2025-12-03",
        },
        ttl_days=90,
    )

    # Test 2: Cache hit
    print("\n--- Test 2: Same query (cache hit) ---")
    result = cache.get(query)
    print(f"Result: {result}")

    # Test 3: Different query (cache miss)
    print("\n--- Test 3: Different query (cache miss) ---")
    query2 = "What Python libraries for finance?"
    result = cache.get(query2)
    print(f"Result: {result}")

    cache.set(
        query2,
        {"answer": "Pandas, NumPy, Matplotlib, yfinance", "source": "knowledge_base"},
    )

    # Test 4: Case insensitive (cache hit)
    print("\n--- Test 4: Case insensitive (cache hit) ---")
    query3 = "WHAT ARE PYTHON FINANCE SALARIES IN EUROPE?"
    result = cache.get(query3)
    print(f"Result: {result}")

    # Stats
    cache.print_stats()

    print("\n" + "=" * 60)
    print("✅ Cache system working!")
    print("=" * 60)
