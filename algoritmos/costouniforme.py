## codigo hecho con la asistencia de gemini

import heapq

def search_ucs_graph(graph, start, exit_pos):
    if start not in graph:
        return [start]

    # Priority queue almacena tuples (costo_acumulado_g, nodo_actual)
    pq = [(0.0, start)]
    g_costs = {start: 0.0}
    parents = {}

    while pq:
        current_g, node = heapq.heappop(pq)

        if node == exit_pos:
            path = []
            curr = exit_pos
            while curr in parents:
                path.append(curr)
                curr = parents[curr]
            path.append(start)
            path.reverse()
            return path

        if current_g > g_costs.get(node, float('inf')):
            continue

        for neighbor, edge_cost in graph.get(node, []):
            new_g = current_g + edge_cost
            if new_g < g_costs.get(neighbor, float('inf')):
                g_costs[neighbor] = new_g
                parents[neighbor] = node
                heapq.heappush(pq, (new_g, neighbor))

    return [start]

