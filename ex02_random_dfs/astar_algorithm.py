from astar import AStar
from math import sqrt
from vs.constants import VS

class AStarExplorer(AStar):
    def __init__(self, graph, start, goal, diagonal_cost, line_cost, map):
        self.graph = graph
        self.start = start
        self.goal = goal
        self.diagonal_cost = diagonal_cost
        self.line_cost = line_cost
        self.map = map

    def neighbors(self, node):
        x, y = node
        print("verificando os vizinhos de: {}".format(node))
        # Define os vizinhos de um nó como as posições adjacentes que não são obstáculos
        neighbors = [(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx != 0 or dy != 0)]
        valid_neighbors = []
        for nx, ny in neighbors:
            # Verifica se o vizinho esta no mapa, ou seja, se foi visitado
            # isso garante que ele nao é nem um obstaculo, nem uma parede
            coordenada = (nx,ny)
            if self.graph[nx][ny] != VS.WALL and self.map.in_map(coordenada):
                valid_neighbors.append((nx, ny))
        print("vizinhos válidos de {} sao: {}".format(node, valid_neighbors))
        return valid_neighbors

    def distance_between(self, n1, n2):
        x1, y1 = n1
        x2, y2 = n2
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        # Custo diferente para movimento em linha ou diagonal
        return self.line_cost if dx == 0 or dy == 0 else self.diagonal_cost

    def heuristic_cost_estimate(self, current, goal):
        # Estima o custo heurístico de um nó até o destino como a distância de Manhattan
        x1, y1 = current
        x2, y2 = goal
        return abs(x2 - x1) + abs(y2 - y1)
    
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
