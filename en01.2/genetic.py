import csv
import random

from read_map import read_matrix, shortest_path

victims = {}
BASE = (65, 22)
TIMELIMIT = 1000
CLUSTER = 4
POPULATION = 10
matrix = read_matrix(90, 90, '../datasets/data_300v_90x90/env_obst.txt')

with open(f'cluster{CLUSTER}.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in reader:
        if row[0] == "ID":
            continue
        victim = {"id": int(row[0])}
        victim["coords"] = eval(f"{row[1:3]}".replace('"', "").replace("'",""))[0]
        victim["coords"] = (victim["coords"][0] + BASE[0], victim["coords"][1] + BASE[1])
        victim["feat"] = eval(f"{row[3:9]}".replace('"', "").replace("'",""))[0]
        victims[victim["id"]] = victim


def get_list_score(victims):
    path_cost = 0
    score = 0
    last_pos = BASE

    out_of_time_victims = []

    for victim in victims:
        c = victim["coords"]
        distance, _ = shortest_path(matrix, last_pos, c)
        last_pos = c
        # print(f"{last_pos} -> {c} = {distance}")
        path_cost += distance

        if not can_return(c, path_cost):
            out_of_time_victims.append(victim)

    score += path_cost
    # print(out_of_time_victims)
    return score


def can_return(current_pos, current_time):
    distance, _ = shortest_path(matrix, current_pos, BASE)
    return (current_time + distance) <= TIMELIMIT


def run_population():
    population = []
    for i in range(POPULATION):
        if i % 10 == 0:
            print(f"Population {i}")

        shuffled_list = list(victims.keys())
        random.shuffle(shuffled_list)
        victims_list = [victims[x] for x in shuffled_list]
        score = get_list_score(victims_list)
        population.append({
            "id": i,
            "score": score,
            "victims": victims_list
        })
    population.sort(key=lambda x: x['score'])
    return population

def run_gen(gen):
    population = run_population()

    csv_population = []
    for p in population:
        csv_population.append({
            "id": p['id'],
            "score": p['score'],
            "victims": ' '.join([str(victim['id']) for victim in p['victims']])
        })

    with open(f'cluster{CLUSTER}-population-gen{gen}.csv', mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["id", "score", "victims"])
        writer.writeheader()
        writer.writerows(csv_population)

    best_pop = population[:int(len(population) / 5)]
    avg_pop = population[int(len(population) / 5):len(population) - int(len(population) / 5)]
    worst_pop = population[len(population) - int(len(population) / 5):]

    selected = []
    selected.extend(best_pop)

    for p in worst_pop:
        if random.random() > 0.9:
            selected.append(p)


def print_ids(population):
    print(' '.join([str(p['id']) for p in population]))

run_gen(0)