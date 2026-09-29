##código realizado con la asistencia de gemini
import random
from collections import deque

def heuristic_manhattan(r, c, dest):
    return abs(r - dest[0]) + abs(c - dest[1])

# --- Metaheurística Bioinspirada: Algoritmo Genético (GA) ---
class GeneticAlgorithmPlanner:
    def __init__(self, env, pop_size=30, generations=20, chromosome_len=40):
        self.env = env
        self.pop_size = pop_size
        self.generations = generations
        self.chrono_len = chromosome_len
        self.dir_map = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    def _decode_path(self, start, chromosome):
        path = [start]
        curr_r, curr_c = start
        for gene in chromosome:
            dr, dc = self.dir_map[gene]
            nr, nc = curr_r + dr, curr_c + dc
            if self.env.is_walkable(nr, nc):
                curr_r, curr_c = nr, nc
            path.append((curr_r, curr_c))
            if (curr_r, curr_c) == self.env.exit_pos:
                break
        return path

    def _fitness(self, chromosome, start):
        path = self._decode_path(start, chromosome)
        final_pos = path[-1]
        dist_to_exit = heuristic_manhattan(final_pos[0], final_pos[1], self.env.exit_pos)
        
        # Calcular penalización de congruencia / congestión
        total_cost = 0.0
        for r, c in path:
            total_cost += self.env.get_step_cost(r, c)

        fit = 1000.0 / (dist_to_exit + 1.0) - total_cost * 0.5
        if final_pos == self.env.exit_pos:
            fit += 2000.0
        return fit

    def plan_agent_path(self, start):
        population = [[random.randint(0, 4) for _ in range(self.chrono_len)] for _ in range(self.pop_size)]

        for _ in range(self.generations):
            scores = [(self._fitness(ind, start), ind) for ind in population]
            scores.sort(key=lambda x: x[0], reverse=True)
            selected = [ind for _, ind in scores[:self.pop_size // 2]]

            next_gen = selected.copy()
            while len(next_gen) < self.pop_size:
                p1, p2 = random.sample(selected, 2)
                cutoff = random.randint(1, self.chrono_len - 1)
                child = p1[:cutoff] + p2[cutoff:]
                if random.random() < 0.2:
                    m_idx = random.randint(0, self.chrono_len - 1)
                    child[m_idx] = random.randint(0, 4)
                next_gen.append(child)
            population = next_gen

        best_chromo = max(population, key=lambda ind: self._fitness(ind, start))
        return self._decode_path(start, best_chromo)