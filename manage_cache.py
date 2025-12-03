"""
Cache Management Tool
Quick commands to manage document cache
"""

import sys
from src.document_cache import DocumentCache


def main():
    cache = DocumentCache()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python manage_cache.py stats     - Show cache statistics")
        print("  python manage_cache.py clear     - Clear all cache")
        print(
            "  python manage_cache.py invalidate <file> - Remove specific file from cache"
        )
        return

    command = sys.argv[1]

    if command == "stats":
        cache.print_stats()

        print(f"\n📋 Cached Files:")
        for filepath, info in cache.index.items():
            print(f"   • {filepath}")
            print(f"     Type: {info['file_type']}, Cached: {info['cached_at']}")

    elif command == "clear":
        print("⚠️  This will delete all cached documents!")
        confirm = input("Continue? (yes/no): ")

        if confirm.lower() == "yes":
            cache.clear_all()
            print("✅ Cache cleared!")
        else:
            print("❌ Cancelled")

    elif command == "invalidate" and len(sys.argv) > 2:
        filepath = sys.argv[2]
        cache.invalidate(filepath)
        print(f"✅ Invalidated: {filepath}")

    else:
        print(f"❌ Unknown command: {command}")


if __name__ == "__main__":
    main()
