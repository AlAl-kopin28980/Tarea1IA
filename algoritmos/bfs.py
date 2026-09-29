##código realizado con la asistencia de gemini
from collections import deque
def search_bfs_graph(graph, start, exit_pos):
    if start not in graph:
        return [start]

    queue = deque([(start, [start])])
    visited = {start}

    while queue:
        node, path = queue.popleft()
        if node == exit_pos:
            return path

        for neighbor, _ in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return [start]

