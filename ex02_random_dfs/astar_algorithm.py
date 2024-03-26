from astar import AStar
from vs.constants import VS

class AStarExplorer(AStar):
    def __init__(self, graph, start, goal):
        self.graph = graph
        self.start = start
        self.goal = goal

    def neighbors(self, node):
        # x, y = node
        # # Define os vizinhos de um nó como as posições adjacentes que não são obstáculos
        # neighbors = [(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx != 0 or dy != 0)]
        # # Desconsidera vizinhos que são paredes ou fora do mapa
        # valid_neighbors = [(nx, ny) for nx, ny in neighbors if 0 <= nx < len(self.graph) and 0 <= ny < len(self.graph[0]) and self.graph[nx][ny] != VS.OBST_WALL]
        # return valid_neighbors
        x, y = node
        # Define os vizinhos de um nó como as posições adjacentes que não são obstáculos
        neighbors = [(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx != 0 or dy != 0)]
        valid_neighbors = []
        for nx, ny in neighbors:
            # Verifica se a posição está dentro dos limites do grafo
            if 0 <= nx < len(self.graph) and 0 <= ny < len(self.graph[0]):
                # Verifica se a posição não é uma parede
                if self.graph[nx][ny] != VS.OBST_WALL:
                    valid_neighbors.append((nx, ny))
        return valid_neighbors

    def distance_between(self, n1, n2):
        # Calcula a distância entre dois nós como a distância de Manhattan
        return abs(n2[0] - n1[0]) + abs(n2[1] - n1[1])

    def heuristic_cost_estimate(self, current, goal):
        # Estima o custo heurístico de um nó até o destino como a distância de Manhattan
        return abs(goal[0] - current[0]) + abs(goal[1] - current[1])
    
    def is_goal_reached(self, current, goal):
        return current == goal

    def find_path(self):
        # Chamada do algoritmo de busca A*
        return self.astar(self.start, self.goal)
