import heapq

import numpy as np


def read_matrix(nx, ny, obstacles_file):
    matrix = np.ones((ny, nx))

    with open(obstacles_file, 'r') as file:
        for line in file:
            y, x, cost = map(float, line.strip().split(','))
            matrix[int(y)][int(x)] = cost

    return matrix


def pretty_print_matrix(matrix):
    for row in matrix:
        print(" ".join(f"{cell:6.2f}" for cell in row))


def shortest_path(matrix, start, end):
    rows, cols = len(matrix), len(matrix[0])
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    if matrix[start[0]][start[1]] == 100 or matrix[end[0]][end[1]] == 100:
        return float('inf'), []

    min_heap = [(0, start)]
    heapq.heapify(min_heap)
    distances = {start: 0}
    previous = {start: None}

    while min_heap:
        current_distance, current_position = heapq.heappop(min_heap)

        if current_position == end:
            break

        for direction in directions:
            row, col = current_position[0] + direction[0], current_position[1] + direction[1]
            if 0 <= row < rows and 0 <= col < cols:
                next_position = (row, col)
                if matrix[row][col] != 100:
                    new_distance = current_distance + matrix[row][col]
                    if next_position not in distances or new_distance < distances[next_position]:
                        distances[next_position] = new_distance
                        previous[next_position] = current_position
                        heapq.heappush(min_heap, (new_distance, next_position))

    if end in previous:
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()
        return distances[end], path
    else:
        return float('inf'), []


# matrix = create_matrix(12, 12, '../datasets/data_10v_12x12/env_obst.txt')
matrix = read_matrix(90, 90, '../datasets/data_300v_90x90/env_obst.txt')

# pretty_print_matrix(matrix)

start_point = (65, 22)
end_point = (65, 21)

distance, path = shortest_path(matrix, start_point, end_point)
# print(f"Shortest distance from {start_point} to {end_point} is {distance}")
# print("Path:", path)
