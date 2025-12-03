"""
Anytype Connector
Week 3 Day 15 - Sync Anytype workspace to RAG system
"""

from typing import List, Dict, Optional
import json
from datetime import datetime
from pathlib import Path

from config import Config

try:
    from anytype import Anytype

    ANYTYPE_AVAILABLE = True
except ImportError:
    ANYTYPE_AVAILABLE = False
    print("⚠️  anytype-client not installed. Run: pip install anytype-client")


class AnytypeConnector:
    """Connect to Anytype and sync objects to RAG"""

    def __init__(self):
        cache_dir = Config.ANYTYPE_CACHE_PATH
        self.api_key = Config.ANYTYPE_API_KEY
        self.space_id = Config.ANYTYPE_SPACE_ID

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.client = None
        self.current_space = None

        # Stats
        self.stats = {"objects_fetched": 0, "objects_synced": 0, "last_sync": None}

        print(f"🔗 Anytype Connector initialized")
        print(f"   Cache dir: {cache_dir}")
        print(f"   API available: {ANYTYPE_AVAILABLE}")

    def authenticate(self):
        """Authenticate with Anytype API"""
        if not ANYTYPE_AVAILABLE:
            print("❌ Anytype client not available")
            return False

        try:
            print("\n🔐 Authenticating with Anytype...")

            # The anytype-client uses interactive auth only (no API key parameter)
            # It will open browser or show a code
            self.client = Anytype()

            # Call auth() method - this will prompt for code or open browser
            print("   ℹ️  This will open your browser or show a code")
            print("   ℹ️  Follow the prompts to authenticate\n")

            self.client.auth()

            print("✅ Authentication successful!")
            return True

        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            print("\n💡 TIP: Make sure Anytype Desktop is running")
            print("   Alternative: Use manual export workflow")
            return False

    def list_spaces(self) -> List[Dict]:
        """List all available spaces"""
        if not self.client:
            print("❌ Not authenticated. Run authenticate() first")
            return []

        try:
            spaces = self.client.get_spaces()

            print(f"\n📚 Available Spaces ({len(spaces)}):")
            for i, space in enumerate(spaces, 1):
                space_name = space.get("name", "Unnamed Space")
                space_id = space.get("id", "unknown")
                print(f"   {i}. {space_name} (ID: {space_id[:8]}...)")

            return spaces

        except Exception as e:
            print(f"❌ Failed to list spaces: {e}")
            return []

    def connect_space(self, space_id: Optional[str] = None):
        """Connect to a specific space (or default)"""
        if not self.client:
            print("❌ Not authenticated")
            return False

        try:
            if space_id:
                self.current_space = self.client.get_space(space_id)
            else:
                # Use default/first space
                spaces = self.client.get_spaces()
                if spaces:
                    self.current_space = spaces[0]
                else:
                    print("❌ No spaces found")
                    return False

            space_name = self.current_space.get("name", "Default Space")
            print(f"✅ Connected to space: {space_name}")
            return True

        except Exception as e:
            print(f"❌ Failed to connect to space: {e}")
            return False

    def fetch_all_objects(self) -> List[Dict]:
        """Fetch all objects from current space"""
        if not self.current_space:
            print("❌ No space connected")
            return []

        try:
            print("\n🔍 Fetching objects from Anytype...")

            # Use search API to get all objects
            # Search with empty query returns all objects
            objects = self.client.search_objects(
                space_id=self.current_space.get("id"),
                query="",  # Empty = all objects
            )

            self.stats["objects_fetched"] = len(objects)

            print(f"✅ Fetched {len(objects)} objects")
            return objects

        except Exception as e:
            print(f"❌ Failed to fetch objects: {e}")
            return []

    def extract_content(self, obj: Dict) -> Dict:
        """Extract content and metadata from Anytype object"""

        # Extract basic info
        obj_id = obj.get("id", "unknown")
        obj_type = obj.get("type", "unknown")

        # Extract title/name
        title = obj.get("name") or obj.get("title") or f"Untitled {obj_type}"

        # Extract main content
        content_parts = []

        # Get description if exists
        if "description" in obj:
            content_parts.append(obj["description"])

        # Get text blocks if exists
        if "blocks" in obj:
            for block in obj["blocks"]:
                if block.get("type") == "text":
                    content_parts.append(block.get("text", ""))

        # Combine all content
        content = "\n\n".join(filter(None, content_parts))

        # Extract tags
        tags = obj.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]

        # Extract metadata
        metadata = {
            "source": "anytype",
            "object_id": obj_id,
            "object_type": obj_type,
            "title": title,
            "tags": tags,
            "created_at": obj.get("createdDate"),
            "modified_at": obj.get("lastModifiedDate"),
        }

        return {"id": obj_id, "title": title, "content": content, "metadata": metadata}

    def sync_to_rag(self, kb, objects: List[Dict]):
        """Sync Anytype objects to RAG knowledge base"""
        print(f"\n📊 Syncing {len(objects)} objects to RAG...")

        synced_count = 0

        for obj in objects:
            try:
                # Extract content
                extracted = self.extract_content(obj)

                # Skip if no content
                if not extracted["content"] or len(extracted["content"]) < 10:
                    continue

                # Clean metadata for ChromaDB (no lists, only str/int/float/bool)
                clean_metadata = {}
                for key, value in extracted["metadata"].items():
                    if isinstance(value, list):
                        # Convert lists to comma-separated strings
                        clean_metadata[key] = (
                            ", ".join(str(v) for v in value) if value else ""
                        )
                    elif isinstance(value, (str, int, float, bool)):
                        clean_metadata[key] = value
                    elif value is None:
                        clean_metadata[key] = ""
                    else:
                        # Convert other types to string
                        clean_metadata[key] = str(value)

                # Add to knowledge base
                doc_id = f"anytype_{extracted['id']}"

                kb.collection.upsert(
                    documents=[extracted["content"]],
                    ids=[doc_id],
                    metadatas=[clean_metadata],
                )

                synced_count += 1
                print(f"   ✓ Synced: {extracted['title']}")

            except Exception as e:
                obj_id = obj.get("id", "unknown")
                print(f"   ⚠️  Failed to sync {obj_id}: {e}")
                continue

        self.stats["objects_synced"] = synced_count
        self.stats["last_sync"] = datetime.now().isoformat()

        print(f"\n✅ Synced {synced_count}/{len(objects)} objects to RAG")

        return synced_count

    def cache_objects(self, objects: List[Dict]):
        """Cache objects to JSON for offline use"""
        cache_file = (
            self.cache_dir
            / f"anytype_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "export_date": datetime.now().isoformat(),
                        "object_count": len(objects),
                        "objects": objects,
                    },
                    f,
                    indent=2,
                )

            print(f"💾 Cached {len(objects)} objects to {cache_file.name}")
            return cache_file

        except Exception as e:
            print(f"❌ Failed to cache: {e}")
            return None

    def load_from_cache(self, cache_file: Optional[str] = None) -> List[Dict]:
        """Load objects from cache"""
        if cache_file:
            file_path = Path(cache_file)
        else:
            # Load most recent cache
            cache_files = sorted(self.cache_dir.glob("anytype_export_*.json"))
            if not cache_files:
                print("❌ No cache files found")
                return []
            file_path = cache_files[-1]

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            objects = data.get("objects", [])
            export_date = data.get("export_date", "unknown")

            print(f"💾 Loaded {len(objects)} objects from cache")
            print(f"   Export date: {export_date}")

            return objects

        except Exception as e:
            print(f"❌ Failed to load cache: {e}")
            return []

    def load_from_export_folder(
        self, export_folder: str = "data/anytype_export"
    ) -> List[Dict]:
        """Load from Anytype manual export (reliable fallback)"""
        export_path = Path(export_folder)

        if not export_path.exists():
            export_path.mkdir(parents=True, exist_ok=True)
            print(f"\n📁 Created export folder: {export_folder}")
            print(f"\n💡 To use Anytype content:")
            print(f"   1. Open Anytype Desktop")
            print(f"   2. Go to Settings > Export")
            print(f"   3. Export as Markdown or JSON")
            print(f"   4. Save to: {export_folder.replace('data/', '')}")
            print(f"   5. Run this script again\n")
            return []

        objects = []

        print(f"\n📂 Scanning export folder: {export_folder}")

        # Load JSON files
        json_files = list(export_path.glob("**/*.json"))
        for file in json_files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                    # Handle different JSON structures
                    if isinstance(data, list):
                        objects.extend(data)
                    else:
                        objects.append(data)

                print(f"   ✓ Loaded: {file.name}")
            except Exception as e:
                print(f"   ⚠️  Failed to load {file.name}: {e}")

        # Load Markdown files
        md_files = list(export_path.glob("**/*.md"))
        for file in md_files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read()

                    # Parse frontmatter if exists
                    import frontmatter

                    try:
                        post = frontmatter.load(file)
                        metadata = post.metadata
                        content = post.content
                    except:
                        metadata = {}

                    objects.append(
                        {
                            "   id": file.stem,
                            "type": metadata.get("type", "Note"),
                            "name": metadata.get(
                                "title", file.stem.replace("-", " ").title()
                            ),
                            "description": content,
                            "tags": metadata.get("tags", []),
                            "createdDate": metadata.get("created"),
                            "lastModifiedDate": metadata.get("modified"),
                        }
                    )

                print(f"   ✓ Loaded: {file.name}")
            except Exception as e:
                print(f"   ⚠️  Failed to load {file.name}: {e}")

        if objects:
            print(f"\n✅ Loaded {len(objects)} objects from export")
        else:
            print(f"\n⚠️  No files found in {export_folder}")
            print(f"   Export some content from Anytype Desktop first!")

        return objects

    def get_stats(self) -> Dict:
        """Get sync statistics"""
        return {
            **self.stats,
            "cache_files": len(list(self.cache_dir.glob("anytype_export_*.json"))),
            "anytype_available": ANYTYPE_AVAILABLE,
        }

    def print_stats(self):
        """Print sync statistics"""
        stats = self.get_stats()

        print(f"\n📊 Anytype Sync Statistics:")
        print(f"   Objects fetched: {stats['objects_fetched']}")
        print(f"   Objects synced: {stats['objects_synced']}")
        print(f"   Last sync: {stats['last_sync'] or 'Never'}")
        print(f"   Cache files: {stats['cache_files']}")
        print(
            f"   API status: {'✅ Available' if stats['anytype_available'] else '❌ Not available'}"
        )


# Demo/Test mode
if __name__ == "__main__":
    print("=" * 70)
    print("🔗 ANYTYPE CONNECTOR DEMO")
    print("=" * 70)

    connector = AnytypeConnector()

    if ANYTYPE_AVAILABLE:
        print("\n--- Test 1: Authentication ---")
        print("ℹ️  This requires:")
        print("   1. Anytype desktop app running")
        print("   2. Settings > API > Generate Code")
        print("   3. Enter 4-digit code when prompted")
        print("\nProceed with authentication? (y/n): ", end="")

        choice = input().strip().lower()

        if choice == "y":
            if connector.authenticate():
                # List spaces
                spaces = connector.list_spaces()

                # Connect to first space
                if spaces:
                    connector.connect_space()

                    # Fetch objects
                    objects = connector.fetch_all_objects()

                    # Show sample
                    if objects:
                        print(f"\n--- Sample Object ---")
                        sample = connector.extract_content(objects[0])
                        print(f"Title: {sample['title']}")
                        print(f"Type: {sample['metadata']['object_type']}")
                        print(f"Content preview: {sample['content'][:100]}...")

                    # Cache for later
                    connector.cache_objects(objects)

                    # Stats
                    connector.print_stats()
        else:
            print("\n⏭️  Skipping authentication test")
    else:
        print("\n--- Test 2: Offline Mode (Cache) ---")
        print("ℹ️  Install anytype-client to enable live sync")
        print("   For now, testing cache functionality...")

        # Create dummy cache for testing
        dummy_objects = [
            {
                "id": "test1",
                "type": "Note",
                "name": "Python Learning Notes",
                "description": "My notes on learning Python for finance",
                "tags": ["python", "learning"],
            },
            {
                "id": "test2",
                "type": "Project",
                "name": "AI Career Coach",
                "description": "Building an AI-powered career coaching system",
                "tags": ["project", "ai"],
            },
        ]

        # Cache dummy data
        cache_file = connector.cache_objects(dummy_objects)

        # Load from cache
        loaded = connector.load_from_cache()

        # Extract content
        for obj in loaded:
            extracted = connector.extract_content(obj)
            print(f"\n   ✓ {extracted['title']}")
            print(f"     Type: {extracted['metadata']['object_type']}")

    print("\n" + "=" * 70)
    print("✅ ANYTYPE CONNECTOR READY!")
    print("=" * 70)
