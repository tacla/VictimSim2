import heapq

from vs.constants import VS


class Position:
    def __init__(self, coords, visited, difficulty=3):
        self.coords = coords
        self.difficulty = difficulty
        self.victim_seq = VS.NO_VICTIM
        self.visited = visited
        self.neighborhood = {}
        self.action_seq = []

    def __str__(self):
        return f"({self.coords[0]},{self.coords[1]})"

    def __lt__(self, other):
        return self.difficulty < other.difficulty


class Map:
    def __init__(self):
        self.positions = {}

    def in_map(self, coord):
        return coord in self.positions

    def get_or_create(self, coord):
        if self.in_map(coord):
            pos = self.get(coord)
        else:
            pos = Position(coords=coord, visited=False)
            self.add(pos)
        return pos

    def get(self, coord) -> Position:
        return self.positions.get(coord)

    def add(self, position):
        if self.visited(position.coords) and self.get(position.coords).difficulty > position.difficulty:
            return

        self.positions[position.coords] = position
        return position

    def extend_map(self, new_map):
        repeated = set(self.positions.keys()).intersection(set(new_map.positions.keys()))

        for r in repeated:
            if len(new_map.positions[r].neighborhood) > len(self.positions[r].neighborhood):
                self.positions[r] = new_map.positions[r]

        for p in new_map.positions:
            if p not in self.positions:
                self.positions[p] = new_map.positions[p]

    def visited(self, coord):
        return coord in self.positions and self.positions[coord].visited

    def get_closest_not_visited(self, pos):
        queue = list(pos.neighborhood.values())
        verified = {}
        while len(queue) != 0:
            p = queue.pop()
            if not p.visited:
                return p

            if p.coords not in verified:
                queue.extend(list(p.neighborhood.values()))
                verified[p.coords] = True
        return None

    def time_to_return(self, actual_pos, explorer):
        path = self.get_path(actual_pos, self.get((0, 0)), explorer)[1:]
        time = 0
        before = actual_pos
        for p in path:
            dx, dy = before.coords[0] - p.coords[0], before.coords[1] - p.coords[1]
            cost = explorer.COST_LINE if dx == 0 or dy == 0 else explorer.COST_DIAG
            time += p.difficulty * cost
        return time

    def get_path(self, actual_pos, wanted_pos, explorer):
        open_list = []
        best_for = {}
        closed_set = set()

        def heuristic(node):
            dx, dy = node.coords[0] - wanted_pos.coords[0], node.coords[1] - wanted_pos.coords[1]
            cost = explorer.COST_LINE if dx == 0 or dy == 0 else explorer.COST_DIAG
            return abs(dx) + abs(dy) * cost

        g_score = {actual_pos: 0}
        f_score = {actual_pos: heuristic(actual_pos)}
        parent = {actual_pos: None}
        path_to_node = {actual_pos: [actual_pos]}
        heapq.heappush(open_list, (f_score[actual_pos], actual_pos))

        while open_list:
            _, current_node = heapq.heappop(open_list)

            if current_node == wanted_pos:
                return path_to_node[current_node]

            closed_set.add(current_node)

            for neighbor in current_node.neighborhood.values():
                if neighbor in closed_set:
                    continue

                dx, dy = current_node.coords[0] - neighbor.coords[0], current_node.coords[1] - neighbor.coords[1]
                cost = explorer.COST_LINE if dx == 0 or dy == 0 else explorer.COST_DIAG

                tentative_g_score = g_score[current_node] + (neighbor.difficulty * cost)
                if neighbor not in open_list or tentative_g_score < g_score[neighbor]:
                    parent[neighbor] = current_node
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor)
                    if neighbor not in open_list and (
                            neighbor not in best_for or best_for[neighbor] > f_score[neighbor]):
                        best_for[neighbor] = f_score[neighbor]
                        heapq.heappush(open_list, (f_score[neighbor], neighbor))
                        path_to_node[neighbor] = path_to_node[current_node] + [neighbor]

        return None

    def draw(self):
        min_x = min(self.positions[key].coords[0] for key in self.positions.keys())
        max_x = max(self.positions[key].coords[0] for key in self.positions.keys())
        min_y = min(self.positions[key].coords[1] for key in self.positions.keys())
        max_y = max(self.positions[key].coords[1] for key in self.positions.keys())

        for y in range(min_y, max_y + 1):
            row = ""
            for x in range(min_x, max_x + 1):
                pos = self.get((x, y))
                if pos:
                    if pos.victim_seq == VS.NO_VICTIM:
                        row += f"[{pos.difficulty:7.2f}  no] "
                    else:
                        row += f"[{pos.difficulty:7.2f} {pos.victim_seq:3d}] "
                else:
                    row += f"[     ?     ] "
            print(row)
