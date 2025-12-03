"""
Document Cache Manager
Week 3 Day 18+ - Speed up document parsing with smart caching
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime


class DocumentCache:
    """Cache parsed documents to avoid re-parsing unchanged files"""

    def __init__(self, cache_dir: str = "data/cache/documents"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Load cache index
        self.index_file = self.cache_dir / "cache_index.json"
        self.index = self._load_index()

        self.stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "files_cached": 0,
            "cache_size_mb": 0,
        }

        print(f"💾 Document Cache initialized")
        print(f"   Cache dir: {cache_dir}")
        print(f"   Cached files: {len(self.index)}")

    def _load_index(self) -> Dict:
        """Load cache index from disk"""
        if self.index_file.exists():
            try:
                with open(self.index_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_index(self):
        """Save cache index to disk"""
        try:
            with open(self.index_file, "w", encoding="utf-8") as f:
                json.dump(self.index, f, indent=2)
        except Exception as e:
            print(f"   ⚠️  Failed to save cache index: {e}")

    def _get_file_hash(self, filepath: Path) -> str:
        """Calculate file hash for change detection"""
        try:
            # Use file size + modified time for quick hash
            stat = filepath.stat()
            content = f"{filepath.name}_{stat.st_size}_{stat.st_mtime}"
            return hashlib.md5(content.encode()).hexdigest()
        except:
            return ""

    def _get_cache_path(self, file_hash: str) -> Path:
        """Get cache file path for a document hash"""
        return self.cache_dir / f"{file_hash}.json"

    def get(self, filepath: str) -> Optional[Dict]:
        """
        Get cached document if available and not changed

        Returns:
            Cached document data or None if not cached/changed
        """
        filepath = Path(filepath)

        if not filepath.exists():
            return None

        # Calculate current file hash
        file_hash = self._get_file_hash(filepath)

        if not file_hash:
            self.stats["cache_misses"] += 1
            return None

        # Check if file is in index
        file_key = str(filepath)

        if file_key in self.index:
            cached_hash = self.index[file_key]["hash"]

            # Check if file changed
            if cached_hash == file_hash:
                # File unchanged - load from cache
                cache_path = self._get_cache_path(file_hash)

                if cache_path.exists():
                    try:
                        with open(cache_path, "r", encoding="utf-8") as f:
                            data = json.load(f)

                        self.stats["cache_hits"] += 1
                        print(f"   ✓ Cache HIT: {filepath.name}")
                        return data
                    except Exception as e:
                        print(f"   ⚠️  Cache read error: {e}")

        self.stats["cache_misses"] += 1
        return None

    def set(self, filepath: str, data: Dict):
        """
        Cache parsed document data

        Args:
            filepath: Original file path
            data: Parsed document data to cache
        """
        filepath = Path(filepath)

        if not filepath.exists():
            return

        # Calculate file hash
        file_hash = self._get_file_hash(filepath)

        if not file_hash:
            return

        try:
            # Save parsed data
            cache_path = self._get_cache_path(file_hash)

            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            # Update index
            file_key = str(filepath)
            self.index[file_key] = {
                "hash": file_hash,
                "cached_at": datetime.now().isoformat(),
                "cache_file": cache_path.name,
                "file_type": data.get("file_type", "unknown"),
            }

            self._save_index()

            self.stats["files_cached"] += 1
            print(f"   💾 Cached: {filepath.name}")

        except Exception as e:
            print(f"   ⚠️  Failed to cache {filepath.name}: {e}")

    def invalidate(self, filepath: str):
        """Remove file from cache"""
        file_key = str(Path(filepath))

        if file_key in self.index:
            # Remove cache file
            file_hash = self.index[file_key]["hash"]
            cache_path = self._get_cache_path(file_hash)

            if cache_path.exists():
                cache_path.unlink()

            # Remove from index
            del self.index[file_key]
            self._save_index()

            print(f"   🗑️  Cache invalidated: {filepath}")

    def clear_all(self):
        """Clear entire cache"""
        count = 0

        for cache_file in self.cache_dir.glob("*.json"):
            if cache_file != self.index_file:
                cache_file.unlink()
                count += 1

        self.index = {}
        self._save_index()

        print(f"   🗑️  Cleared {count} cached files")

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        # Calculate cache size
        cache_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.json")) / (
            1024 * 1024
        )  # Convert to MB

        hit_rate = (
            (
                self.stats["cache_hits"]
                / (self.stats["cache_hits"] + self.stats["cache_misses"])
                * 100
            )
            if (self.stats["cache_hits"] + self.stats["cache_misses"]) > 0
            else 0
        )

        return {
            **self.stats,
            "cache_size_mb": round(cache_size, 2),
            "hit_rate": round(hit_rate, 1),
            "total_cached_files": len(self.index),
        }

    def print_stats(self):
        """Print cache statistics"""
        stats = self.get_stats()

        print(f"\n📊 Document Cache Statistics:")
        print(f"   Cache hits: {stats['cache_hits']}")
        print(f"   Cache misses: {stats['cache_misses']}")
        print(f"   Hit rate: {stats['hit_rate']}%")
        print(f"   Total cached files: {stats['total_cached_files']}")
        print(f"   Cache size: {stats['cache_size_mb']} MB")


# Quick test
if __name__ == "__main__":
    cache = DocumentCache()

    print("\n--- Testing Document Cache ---")

    # Test caching
    test_data = {
        "filename": "test.pdf",
        "content": "This is test content",
        "file_type": "pdf",
        "word_count": 100,
    }

    cache.set("data/pdfs/test.pdf", test_data)

    # Test retrieval
    cached = cache.get("data/pdfs/test.pdf")

    if cached:
        print(f"✅ Cache working! Retrieved: {cached['filename']}")

    cache.print_stats()
