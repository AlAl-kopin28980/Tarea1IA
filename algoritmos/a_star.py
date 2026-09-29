## código hecho con la asistencia de gemini
import heapq
import heapq
from collections import deque

def heuristic_manhattan(r, c, dest):
    return abs(r - dest[0]) + abs(c - dest[1])

def search_a_star(env, start):
    dest = env.exit_pos
    open_set = []
    heapq.heappush(open_set, (0.0, start[0], start[1]))
    
    g_score = {start: 0.0}
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
            if not env.is_walkable(nr, nc):
                continue

            cost = env.get_step_cost(nr, nc)
            tentative_g = g_score[(r, c)] + cost

            if tentative_g < g_score.get((nr, nc), float('inf')):
                parents[(nr, nc)] = (r, c)
                g_score[(nr, nc)] = tentative_g
                f = tentative_g + heuristic_manhattan(nr, nc, dest)
                heapq.heappush(open_set, (f, nr, nc))

    return [start]

