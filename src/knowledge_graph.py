"""
Knowledge Graph Builder
Week 2 Day 10 - Build graph from wikilinks in Obsidian notes
"""

from rag_engine import KnowledgeBase
from markdown_parser import MarkdownParser
from typing import Dict, List, Set, Optional
import os
from collections import defaultdict, deque


class KnowledgeGraph:
    """Build and query knowledge graph from wikilinks"""

    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        self.parser = MarkdownParser()

        # Graph structure: {node: [connected_nodes]}
        self.graph = defaultdict(list)

        # Node metadata: {node: {type, tags, content_preview}}
        self.nodes = {}

        # Reverse index: {target: [sources that link to it]}
        self.backlinks = defaultdict(list)

        print("🕸️  Knowledge Graph initialized")

    def build_from_vault(self, vault_path: str):
        """Build graph by scanning Obsidian vault"""
        print(f"\n🔍 Scanning vault: {vault_path}")

        folders_to_scan = ["daily", "skills", "goals", "research", "projects"]
        total_nodes = 0
        total_edges = 0

        for folder in folders_to_scan:
            folder_path = os.path.join(vault_path, folder)

            # Resolve symlink if exists
            real_path = os.path.realpath(folder_path)

            if not os.path.exists(real_path):
                continue

            print(f"   Scanning: {folder}/")

            for filename in os.listdir(real_path):
                if not filename.endswith(".md"):
                    continue

                filepath = os.path.join(real_path, filename)
                self._add_note_to_graph(filepath, folder)
                total_nodes += 1

        # Count edges
        for node, connections in self.graph.items():
            total_edges += len(connections)

        print(f"\n✅ Graph built:")
        print(f"   Nodes: {total_nodes}")
        print(f"   Edges: {total_edges}")
        print(f"   Unique concepts: {len(self.nodes)}")

        return self

    def _add_note_to_graph(self, filepath: str, folder: str):
        """Add single note to graph"""
        parsed = self.parser.parse_file(filepath)
        if not parsed:
            return

        # Create node ID (clean name)
        node_id = self._create_node_id(parsed["filename"], folder)

        # Store node metadata
        self.nodes[node_id] = {
            "type": folder,
            "filename": parsed["filename"],
            "tags": parsed.get("tags", []),
            "metadata": parsed.get("metadata", {}),
            "preview": parsed["content"][:100] + "..." if parsed["content"] else "",
        }

        # Extract wikilinks and create edges
        wikilinks = parsed.get("wikilinks", [])

        for link in wikilinks:
            # Parse link (handle "Skills/Python" or just "Python")
            target_id = self._normalize_wikilink(link)

            # Add edge
            if target_id not in self.graph[node_id]:
                self.graph[node_id].append(target_id)

            # Add backlink
            if node_id not in self.backlinks[target_id]:
                self.backlinks[target_id].append(node_id)

    def _create_node_id(self, filename: str, folder: str) -> str:
        """Create consistent node ID"""
        clean_name = filename.replace(".md", "")
        return f"{folder}/{clean_name}"

    def _normalize_wikilink(self, link: str) -> str:
        """Normalize wikilink to node ID format"""
        # Handle "Skills/Python" or "Python" → "skills/Python"
        if "/" in link:
            parts = link.split("/")
            folder = parts[0].lower()
            name = "/".join(parts[1:])
            return f"{folder}/{name}"
        else:
            # Guess folder based on common patterns
            return self._guess_node_folder(link)

    def _guess_node_folder(self, name: str) -> str:
        """Guess folder for node without path"""
        # Simple heuristic - can be improved
        name_lower = name.lower()

        if any(keyword in name_lower for keyword in ["python", "sql", "git", "pandas"]):
            return f"skills/{name}"
        elif "freelance" in name_lower or "goal" in name_lower:
            return f"goals/{name}"
        elif "project" in name_lower:
            return f"projects/{name}"
        else:
            return f"general/{name}"

    def get_connections(self, node_id: str) -> Dict:
        """Get all connections for a node"""
        return {
            "outgoing": self.graph.get(node_id, []),
            "incoming": self.backlinks.get(node_id, []),
            "metadata": self.nodes.get(node_id, {}),
        }

    def find_path(self, start: str, end: str) -> Optional[List[str]]:
        """Find shortest path between two nodes (BFS)"""
        if start not in self.nodes or end not in self.nodes:
            return None

        # BFS to find shortest path
        queue = deque([(start, [start])])
        visited = {start}

        while queue:
            current, path = queue.popleft()

            if current == end:
                return path

            # Check BOTH outgoing AND incoming connections (bidirectional)
            neighbors = set(self.graph.get(current, [])) | set(
                self.backlinks.get(current, [])
            )

            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None  # No path found

    def find_related_nodes(self, node_id: str, max_depth: int = 2) -> Set[str]:
        """Find all nodes within N hops"""
        if node_id not in self.nodes:
            return set()

        related = set()
        queue = deque([(node_id, 0)])
        visited = {node_id}

        while queue:
            current, depth = queue.popleft()

            if depth > max_depth:
                continue

            if depth > 0:  # Don't include starting node
                related.add(current)

            # Explore neighbors (outgoing + incoming)
            neighbors = self.graph.get(current, []) + self.backlinks.get(current, [])

            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, depth + 1))

        return related

    def get_node_stats(self) -> Dict:
        """Get graph statistics"""
        # Most connected nodes
        connection_counts = {}
        for node in self.nodes.keys():
            outgoing = len(self.graph.get(node, []))
            incoming = len(self.backlinks.get(node, []))
            connection_counts[node] = outgoing + incoming

        top_nodes = sorted(connection_counts.items(), key=lambda x: x[1], reverse=True)[
            :5
        ]

        # Nodes by type
        type_counts = defaultdict(int)
        for node_data in self.nodes.values():
            type_counts[node_data["type"]] += 1

        return {
            "total_nodes": len(self.nodes),
            "total_edges": sum(len(edges) for edges in self.graph.values()),
            "top_connected": top_nodes,
            "nodes_by_type": dict(type_counts),
            "isolated_nodes": [
                n
                for n in self.nodes
                if not self.graph.get(n) and not self.backlinks.get(n)
            ],
        }

    def visualize_connections(self, node_id: str, max_depth: int = 1):
        """Text-based visualization of connections"""
        print(f"\n🕸️  Connections for: {node_id}")
        print("=" * 60)

        if node_id not in self.nodes:
            print("   ⚠️ Node not found")
            return

        # Show metadata
        node_data = self.nodes[node_id]
        print(f"   Type: {node_data['type']}")
        print(f"   Tags: {', '.join(node_data.get('tags', []))}")

        # Outgoing links
        outgoing = self.graph.get(node_id, [])
        if outgoing:
            print(f"\n   → Links to ({len(outgoing)}):")
            for link in outgoing[:5]:  # Show max 5
                link_type = self.nodes.get(link, {}).get("type", "unknown")
                print(f"      • {link} ({link_type})")

        # Incoming links (backlinks)
        incoming = self.backlinks.get(node_id, [])
        if incoming:
            print(f"\n   ← Linked from ({len(incoming)}):")
            for link in incoming[:5]:
                link_type = self.nodes.get(link, {}).get("type", "unknown")
                print(f"      • {link} ({link_type})")

        # Related nodes (2 hops)
        if max_depth > 1:
            related = self.find_related_nodes(node_id, max_depth=2)
            if related:
                print(f"\n   🔗 Related nodes (2 hops): {len(related)}")
                for rel in list(related)[:5]:
                    print(f"      • {rel}")

        print("=" * 60)


# Quick test
if __name__ == "__main__":
    kb = KnowledgeBase()
    graph = KnowledgeGraph(kb)

    # Build graph from vault
    VAULT_PATH = "data/obsidian_vault"
    graph.build_from_vault(VAULT_PATH)

    # Show stats
    print("\n📊 Graph Statistics:")
    stats = graph.get_node_stats()
    print(f"   Total nodes: {stats['total_nodes']}")
    print(f"   Total edges: {stats['total_edges']}")

    if stats["top_connected"]:
        print(f"\n   🏆 Most connected nodes:")
        for node, count in stats["top_connected"]:
            print(f"      {node}: {count} connections")

    print(f"\n   📁 Nodes by type:")
    for node_type, count in stats["nodes_by_type"].items():
        print(f"      {node_type}: {count} nodes")

    # Visualize a node
    if stats["total_nodes"] > 0:
        # Try to visualize Python skill
        graph.visualize_connections("skills/Python", max_depth=2)
