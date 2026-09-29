from collections import deque
import numpy as np
from algoritmos.a_star import search_a_star
from algoritmos.bfs import search_bfs_graph
from algoritmos.costouniforme import search_ucs_graph
from algoritmos.genetic_alg import GeneticAlgorithmPlanner
from algoritmos.greedybfs import search_gbfs
import random

# ==========================================
# 1. ENTORNO Y PROPAGACIÓN DE FUEGO CORREGIDA
# ==========================================
EMPTY = 0
WALL = 1
FIRE = 2
EXIT = 3

class EvacuationEnvironment:
    def __init__(self, grid_map, fire_spread_k=2, cell_capacity=2, penalty_factor=2.0):
        self.initial_grid = np.array(grid_map, dtype=int)
        self.rows, self.cols = self.initial_grid.shape
        self.fire_spread_k = fire_spread_k # Propaga cada k turnos
        self.cell_capacity = cell_capacity
        self.penalty_factor = penalty_factor
        self.reset()

    def reset(self, fire_sources=None):
        self.grid = np.copy(self.initial_grid)
        self.occupancy = np.zeros((self.rows, self.cols), dtype=int)
        self.turn = 0
        
        exits = np.argwhere(self.grid == EXIT)
        if len(exits) == 0:
            raise ValueError("El mapa debe contener una casilla EXIT (3).")
        self.exit_pos = tuple(exits[0])
        
        # Focos de fuego iniciales
        if fire_sources:
            for fr, fc in fire_sources:
                if self.grid[fr, fc] != WALL:
                    self.grid[fr, fc] = FIRE

    def is_valid(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_walkable(self, r, c):
        return self.is_valid(r, c) and self.grid[r, c] != WALL and self.grid[r, c] != FIRE

    def get_step_cost(self, r, c):
        occ = self.occupancy[r, c]
        if occ <= self.cell_capacity:
            return 1.0
        else:
            return 1.0 + self.penalty_factor * ((occ - self.cell_capacity) ** 2)

    def spread_fire(self):
        """
        Propagación corregida: El fuego avanza en 8 direcciones y consume
        cualquier casilla transitable (evitando solo paredes de estructura y salidas).
        """
        if self.turn == 0 or self.turn % self.fire_spread_k != 0:
            return

        fire_cells = np.argwhere(self.grid == FIRE)
        new_fire = set()
        
        # Formas en que se puede mover
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for r, c in fire_cells:
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if self.is_valid(nr, nc):
                    # El fuego consume todo excepto paredes físicas (1)
                    if self.grid[nr, nc] != WALL:
                        if random.random() < 0.5: #el fuego se expande de forma aleatoria
                            new_fire.add((nr, nc))

        for r, c in new_fire:
            self.grid[r, c] = FIRE



def grid_to_graph(env):
    graph = {}
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    for r in range(env.rows):
        for c in range(env.cols):
            if env.is_walkable(r, c):
                neighbors = []
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if env.is_walkable(nr, nc):
                        cost = env.get_step_cost(nr, nc)
                        neighbors.append(((nr, nc), cost))
                
                # Acción de esperar
                wait_cost = env.get_step_cost(r, c)
                neighbors.append(((r, c), wait_cost))
                graph[(r, c)] = neighbors

    return graph


# ==========================================
# 3. SIMULACIÓN CON DETECCIÓN DOBLE DE BAJAS
# ==========================================

class EvacuationSimulation:
    def __init__(self, env, num_agents, start_cell=(2, 2), algorithm_type="A*"):
        self.env = env
        self.num_agents = num_agents
        self.start_cell = start_cell  # Celda fija para todos los agentes
        self.algo = algorithm_type
        self.escaped_count = 0
        self.casualties_count = 0

    def _spawn_agents(self):
        # Asigna la misma celda inicial a todos los agentes
        if not self.env.is_walkable(self.start_cell[0], self.start_cell[1]):
            raise ValueError(f"La celda inicial {self.start_cell} es una pared o fuego.")
        return [self.start_cell for _ in range(self.num_agents)]
    

    def run(self, max_turns=100):
        starts = self._spawn_agents()
        active_agents = {i: pos for i, pos in enumerate(starts)}
        
        graph = grid_to_graph(self.env)
        
        agent_paths = {}
        for i, pos in active_agents.items():
            if self.algo == "BFS":
                agent_paths[i] = search_bfs_graph(graph, pos, self.env.exit_pos)
            elif self.algo == "UCS":
                agent_paths[i] = search_ucs_graph(graph, pos, self.env.exit_pos)
            elif self.algo == "A*":
                agent_paths[i] = search_a_star(self.env, pos)
            elif self.algo == "GBFS":
                agent_paths[i] = search_gbfs(self.env, pos)
            elif self.algo == "GA":
                ga_planner = GeneticAlgorithmPlanner(self.env)
                agent_paths[i] = ga_planner.plan_agent_path(pos)

        step_indices = {i: 0 for i in active_agents}

        for turn in range(1, max_turns + 1):
            if not active_agents:
                break

            self.env.turn = turn
            self.env.occupancy.fill(0)
            graph = grid_to_graph(self.env)

            to_remove = []

            # PASO 1: Movimiento de agentes
            for agent_id, pos in list(active_agents.items()):
                path = agent_paths[agent_id]
                s_idx = step_indices[agent_id]

                if s_idx + 1 < len(path):
                    next_pos = path[s_idx + 1]
                    
                    # Replanificar si el siguiente paso se volvió intransitable por fuego
                    if not self.env.is_walkable(next_pos[0], next_pos[1]):
                        if self.algo in ["BFS", "UCS"]:
                            func = search_bfs_graph if self.algo == "BFS" else search_ucs_graph
                            new_p = func(graph, pos, self.env.exit_pos)
                        else:
                            new_p = search_a_star(self.env, pos)

                        agent_paths[agent_id] = new_p
                        step_indices[agent_id] = 0
                        path = new_p
                        s_idx = 0
                        next_pos = path[1] if len(path) > 1 else pos

                    new_pos = next_pos
                    step_indices[agent_id] += 1
                else:
                    new_pos = pos

                # Si intenta caminar directo hacia el fuego
                if self.env.grid[new_pos[0], new_pos[1]] == FIRE:
                    self.casualties_count += 1
                    to_remove.append(agent_id)
                    continue

                if new_pos == self.env.exit_pos:
                    self.escaped_count += 1
                    to_remove.append(agent_id)
                    continue

                active_agents[agent_id] = new_pos
                self.env.occupancy[new_pos[0], new_pos[1]] += 1

            for aid in to_remove:
                del active_agents[aid]

            # PASO 2: El fuego se propaga en la grilla
            self.env.spread_fire()

            # PASO 3: Detección de bajas por atrapamiento (agentes que el fuego alcanzó)
            burned_agents = []
            for agent_id, pos in active_agents.items():
                if self.env.grid[pos[0], pos[1]] == FIRE:
                    burned_agents.append(agent_id)

            for aid in burned_agents:
                self.casualties_count += 1
                del active_agents[aid]

        return self.escaped_count, turn


def run_benchmark(grid_map, fire_starts, num_agents=10, iterations=80):
    algorithms = ["BFS", "UCS", "A*", "GBFS", "GA"]
    results = {}

    for algo in algorithms:
        survivor_rates = []
        completion_turns = []

        for _ in range(iterations):
            env = EvacuationEnvironment(grid_map, fire_spread_k=2, cell_capacity=2)
            env.reset(fire_sources=fire_starts)

            sim = EvacuationSimulation(env, num_agents=num_agents, algorithm_type=algo)
            escaped, turns = sim.run(max_turns=120)

            rate = (escaped / num_agents) * 100.0
            survivor_rates.append(rate)
            completion_turns.append(turns)

        results[algo] = {
            "rate_mean": np.mean(survivor_rates),
            "turn_mean": np.mean(completion_turns),
            "turn_std": np.std(completion_turns),
            "turn_min": np.min(completion_turns),
            "turn_max": np.max(completion_turns)
        }

    print(f"\n{'Algoritmo':<10} | {'Supervivencia (%)':<18} | {'Media (Turnos)':<15} | {'Std':<8} | {'Min':<5} | {'Max':<5}")
    print("-" * 72)
    for algo, res in results.items():
        print(f"{algo:<10} | {res['rate_mean']:<18.2f} | {res['turn_mean']:<15.2f} | {res['turn_std']:<8.2f} | {res['turn_min']:<5} | {res['turn_max']:<5}")
