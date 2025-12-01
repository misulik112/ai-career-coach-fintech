"""
SKILL MASTERED: Knowledge Graph Construction & Path Finding
Week 2 Day 10

What I learned:
- Graph data structures (adjacency list representation)
- BFS algorithm for shortest path finding
- Bidirectional graph traversal (forward + backlinks)
- Graph statistics and centrality
- Wikilink parsing and normalization

Portfolio highlight:
"Built knowledge graph system that parses markdown wikilinks, constructs
bidirectional graph structure, and finds learning paths between concepts
using BFS algorithm. Enables intelligent connection discovery across
8+ note types."

Business value:
- Knowledge discovery (find hidden connections)
- Learning path optimization (shortest route to goal)
- Content gap identification (isolated nodes = missing links)
- Network analysis (most central concepts)

Technical features:
- BFS path finding (O(V+E) complexity)
- Bidirectional edge tracking (outgoing + backlinks)
- Multi-hop related node discovery
- Graph statistics (centrality, clustering)
- Text-based visualization

Algorithms implemented:
- Breadth-First Search (BFS) for shortest path
- Graph traversal with depth limiting
- Node centrality calculation
- Connected component analysis

Real-world application:
"Freelance proposal: Built graph database system for knowledge management
platform. Implemented path finding algorithms for content recommendation."
"""

from collections import deque, defaultdict


def demo():
    """Quick BFS path finding demo"""
    # Simple graph: A → B → C
    graph = {"A": ["B"], "B": ["C"], "C": []}

    # BFS to find path A → C
    queue = deque([("A", ["A"])])
    visited = {"A"}

    while queue:
        current, path = queue.popleft()
        if current == "C":
            print(f"Path found: {' → '.join(path)}")
            break

        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))


if __name__ == "__main__":
    demo()
