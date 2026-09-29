##código realizado con la asistencia de gemini
import heapq
from collections import deque

def heuristic_manhattan(r, c, dest):
    return abs(r - dest[0]) + abs(c - dest[1])

# --- Búsqueda Informada 2: Greedy Best-First Search ---
def search_gbfs(env, start):
    dest = env.exit_pos
    open_set = []
    heapq.heappush(open_set, (heuristic_manhattan(start[0], start[1], dest), start[0], start[1]))
    visited = {start}
    parents = {}

    directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)]

    while open_set:
        _, r, c = heapq.heappop(open_set)

        if (r, c) == dest:
            path = []
            curr = dest
            while curr in parents:
                path.append(curr)
                curr = parents[curr]
            path.append(start)
            path.reverse()
            return path

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if env.is_walkable(nr, nc) and (nr, nc) not in visited:
                visited.add((nr, nc))
                parents[(nr, nc)] = (r, c)
                h = heuristic_manhattan(nr, nc, dest)
                heapq.heappush(open_set, (h, nr, nc))

    return [start]