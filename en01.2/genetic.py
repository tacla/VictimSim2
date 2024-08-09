import csv
import random
from datetime import datetime
from functools import lru_cache

from read_map import read_matrix, shortest_path

victims = {}
BASE = (65, 22)
TIMELIMIT = 1000
CLUSTER = 4
POPULATION = 200
GENERATIONS = 100
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


@lru_cache(maxsize=None)
def cached_shortest_path(start, end):
    return shortest_path(matrix, start, end)


def get_list_score(victims):
    path_cost = 0
    score = 0
    last_pos = BASE

    out_of_time_victims = []

    for victim in victims:
        c = victim["coords"]
        distance, _ = cached_shortest_path(last_pos, c)
        last_pos = c
        # log(f"{last_pos} -> {c} = {distance}")
        path_cost += distance

        if not can_return(c, path_cost):
            out_of_time_victims.append(victim)

    score += path_cost
    # log(out_of_time_victims)
    return score


def can_return(current_pos, current_time):
    distance, _ = shortest_path(matrix, current_pos, BASE)
    return (current_time + distance) <= TIMELIMIT


def run_population():
    population = []
    for i in range(POPULATION):
        if i % 100 == 0:
            log(f"\t{i} / {POPULATION}")
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


def calculate_score(population):
    for i, p in enumerate(population):
        if i % 100 == 0:
            log(f"\t{i} / {len(population)}")
        p['score'] = get_list_score(p['victims'])
    population.sort(key=lambda x: x['score'])


def run_gen(gen, population = None):
    if not population:
        population = run_population()
    else:
        calculate_score(population)

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
    selected.extend(avg_pop)

    for p in worst_pop:
        if random.random() > 0.9:
            selected.append(p)

    log(f"Crossovering generation {gen}")
    crossovered = crossover_population(selected, len(population) - len(best_pop))
    crossovered.extend(best_pop)

    csv_population = []
    for p in crossovered:
        csv_population.append({
            "id": p['id'],
            "victims": ' '.join([str(victim['id']) for victim in p['victims']])
        })

    with open(f'./crossover/cluster{CLUSTER}-crossover-gen{gen}.csv', mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["id", "victims"])
        writer.writeheader()
        writer.writerows(csv_population)

    log(f"Mutating generation {gen}")
    mutated = mutate_population(crossovered)

    csv_population = []
    for p in mutated:
        csv_population.append({
            "id": p['id'],
            "victims": ' '.join([str(victim['id']) for victim in p['victims']])
        })

    with open(f'./mutated/cluster{CLUSTER}-mutated-gen{gen}.csv', mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["id", "victims"])
        writer.writeheader()
        writer.writerows(csv_population)

    return mutated


def mutate_population(population, mutation_rate=0.2):
    mutated_population = []

    for individual in population:
        if random.random() < mutation_rate:
            victims = individual['victims']
            if len(victims) > 1:
                idx1, idx2 = random.sample(range(len(victims)), 2)
                victims[idx1], victims[idx2] = victims[idx2], victims[idx1]

            mutated_individual = {'id': individual['id'], 'victims': victims}
            mutated_population.append(mutated_individual)
        else:
            mutated_population.append(individual)

    return mutated_population


def crossover_population(population, total):
    offspring = []

    while len(offspring) < total:
        parent1, parent2 = random.sample(population, 2)

        victims1 = parent1['victims']
        victims2 = parent2['victims']

        crossover_point = random.randint(1, len(victims1) - 1)

        child1_victims = victims1[:crossover_point] + victims2[crossover_point:]
        child2_victims = victims2[:crossover_point] + victims1[crossover_point:]

        child1 = {'id': random.randint(0, 1e6), 'victims': child1_victims}
        child2 = {'id': random.randint(0, 1e6), 'victims': child2_victims}

        offspring.append(child1)
        offspring.append(child2)

    return offspring[:total]


def print_ids(population):
    log(' '.join([str(p['id']) for p in population]))


def log(msg):
    print(f"[{datetime.now()}] {msg}")

pop = None
for i in range(GENERATIONS):
    log(f"Running generation {i}")
    pop = run_gen(i, pop)
