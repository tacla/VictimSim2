from math import sqrt

from vs.constants import VS
import heapq

class Map:
    def __init__(self):
        self.positions = {}

    def in_map(self, coord):
        return coord in self.positions

    def size(self):
        return len(self.positions)

    def get_or_create(self, coord):
        if self.in_map(coord):
            pos = self.get(coord)
        else:
            pos = Position(coords=coord, visited=False)
            self.add(pos)
        return pos
    def get(self, coord):
        return self.positions.get(coord)

    def add(self, position):
        if self.visited(position.coords) and self.get(position.coords).difficulty > position.difficulty:
            return

        self.positions[position.coords] = position
        return position

    def visited(self, coord):
        return coord in self.positions and self.positions[coord].visited

    def get_closest_not_visited(self, pos):
        queue = list(pos.neighborhood.values())
        verified = {}
        while len(queue) != 0:
            p = queue.pop()
            if not p.visited and p.difficulty <= 3:
                return p

            if p.coords not in verified:
                queue.extend(list(p.neighborhood.values()))
                verified[p.coords] = True
        return None

    def time_to_return(self, actual_pos, explorer):
        path = self.get_path(actual_pos, self.get((0,0)), explorer)[1:]
        time = 0
        before = actual_pos
        for p in path:
            dx, dy = before.coords[0] - p.coords[0], before.coords[1] - p.coords[1]
            cost = explorer.COST_LINE if dx == 0 or dy == 0 else explorer.COST_DIAG
            time += p.difficulty * cost
        return time

    def get_path(self, actual_pos, wanted_pos, explorer):
        open_list = []
        closed_set = set()

        def heuristic(node):
            return abs(node.coords[0] - wanted_pos.coords[0]) + abs(node.coords[1] - wanted_pos.coords[1])

        actual_pos.g_score = 0
        actual_pos.f_score = heuristic(actual_pos)
        heapq.heappush(open_list, (actual_pos.f_score, actual_pos))
        actual_pos.parent = None

        while open_list:
            _, current_node = heapq.heappop(open_list)

            if current_node == wanted_pos:
                path = []
                while current_node:
                    path.append(current_node)
                    current_node = current_node.parent
                return path[::-1]

            closed_set.add(current_node)

            for neighbor in current_node.neighborhood.values():
                if neighbor in closed_set:
                    continue

                dx, dy = current_node.coords[0] - neighbor.coords[0], current_node.coords[1] - neighbor.coords[1]
                cost = explorer.COST_LINE if dx == 0 or dy == 0 else explorer.COST_DIAG

                tentative_g_score = current_node.g_score + (neighbor.difficulty * cost)
                if neighbor not in open_list or tentative_g_score < neighbor.g_score:
                    neighbor.parent = current_node
                    neighbor.g_score = tentative_g_score
                    neighbor.f_score = tentative_g_score + heuristic(neighbor)
                    if neighbor not in open_list:
                        heapq.heappush(open_list, (neighbor.f_score, neighbor))

        return None

    def draw(self):
        print("TODO o draw")
        return
        if not self.map_data:
            print("Map is empty.")
            return

        min_x = min(key[0] for key in self.map_data.keys())
        max_x = max(key[0] for key in self.map_data.keys())
        min_y = min(key[1] for key in self.map_data.keys())
        max_y = max(key[1] for key in self.map_data.keys())

        for y in range(min_y, max_y + 1):
            row = ""
            for x in range(min_x, max_x + 1):
                item = self.get((x, y))
                if item:
                    if item[1] == VS.NO_VICTIM:
                        row += f"[{item[0]:7.2f}  no] "
                    else:
                        row += f"[{item[0]:7.2f} {item[1]:3d}] "
                else:
                    row += f"[     ?     ] "
            print(row)

class Position:
    def __init__(self, coords, visited, difficulty = 3):
        self.coords = coords
        self.difficulty = difficulty
        self.victim_seq = VS.NO_VICTIM
        self.visited = visited
        self.neighborhood = {}

    def __str__(self):
        return f"({self.coords[0]},{self.coords[1]})"

    def __lt__(self, other):
        return self.difficulty < other.difficulty
    # def __str__(self):
    #     return f"({self.coords[0]}, {self.coords[1]}) - Difficulty: {self.difficulty} - Visited: {self.visited} - Neighborhood: {len(self.neighborhood)} - Victim Seq {self.victim_seq}"