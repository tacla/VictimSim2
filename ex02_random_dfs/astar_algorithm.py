from astar import AStar
from math import sqrt
from vs.constants import VS

class AStarExplorer(AStar):
    def __init__(self, graph, start, goal):
        self.graph = graph
        self.start = start
        self.goal = goal

    def neighbors(self, node):
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
        # Calcula a distância entre dois nós como a distância euclidiana
        x1, y1 = n1
        x2, y2 = n2
        return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def heuristic_cost_estimate(self, current, goal):
        # Estima o custo heurístico de um nó até o destino como a distância euclidiana
        x1, y1 = current
        x2, y2 = goal
        return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
    def is_goal_reached(self, current, goal):
        return current == goal

    def find_path(self):
        # Chamada do algoritmo de busca A*
        path = self.astar(self.start, self.goal)
        if path is None:
            # Se o caminho não foi encontrado, retorne uma lista vazia
            return []
        else:
            return list(path)
