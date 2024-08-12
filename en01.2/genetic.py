import csv
import random
from datetime import datetime

from read_map import read_matrix, shortest_path

victims = {}
BASE = (65, 22)
TIMELIMIT = 1000
CLUSTER = 4
POPULATION = 10_000
GENERATIONS = 1_000
MUTATION_RATE = 0.25
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

cache = {}
def cached_shortest_path(start, end):
    if (start, end) in cache:
        return cache[(start, end)]
    distance, _ = shortest_path(matrix, start, end)
    cache[(start, end)] = distance
    return distance


def get_list_score(victims):
    path_cost = 0
    score = 0
    last_pos = BASE

    out_of_time_victims = []

    for victim in victims:
        c = victim["coords"]
        distance = cached_shortest_path(last_pos, c)
        last_pos = c
        # log(f"{last_pos} -> {c} = {distance}")
        path_cost += distance

        if not can_return(c, path_cost):
            out_of_time_victims.append(victim)

    distance = cached_shortest_path(last_pos, BASE)
    path_cost += distance
    score += path_cost
    # log(out_of_time_victims)
    return score


def can_return(current_pos, current_time):
    distance = cached_shortest_path(current_pos, BASE)
    return (current_time + distance) <= TIMELIMIT


def run_population():
    population = []
    for i in range(POPULATION):
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
        p['score'] = get_list_score(p['victims'])
    population.sort(key=lambda x: x['score'])


def run_gen(gen, population = None):
    if not population:
        population = run_population()
    else:
        calculate_score(population)

    for p in population:
        if len(set([victim['id'] for victim in p['victims']])) != len(p['victims']):
            log(f"Duplicate victims in population {p['id']}")
            raise Exception("Duplicate victims")

    if gen % 100 == 0:
        csv_population = []

        for p in population:
            csv_population.append({
                "id": p['id'],
                "score": p['score'],
                "victims": ' '.join([str(victim['id']) for victim in p['victims']])
            })
        with open(f'./cluster{CLUSTER}/cluster{CLUSTER}-population-gen{gen}.csv', mode='w', newline='') as file:
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

    # log(f"Crossovering generation {gen}")
    crossovered = crossover_population(selected, len(population) - len(best_pop))
    crossovered.extend(best_pop)

    mutated = mutate_population(crossovered)

    return mutated


def mutate_population(population):
    mutated_population = []

    for individual in population:
        if random.random() < MUTATION_RATE:
            victims = individual['victims']
            if len(victims) > 1:
                idx1, idx2 = random.sample(range(len(victims)), 2)
                victims[idx1], victims[idx2] = victims[idx2], victims[idx1]

            mutated_individual = {'id': individual['id'], 'victims': victims}
            mutated_population.append(mutated_individual)
        else:
            mutated_population.append(individual)

    return mutated_population


def order_crossover(parent1, parent2):
    size = len(parent1['victims'])

    start, end = sorted(random.sample(range(size), 2))

    child1_victims = [None] * size
    child2_victims = [None] * size

    child1_victims[start:end] = parent1['victims'][start:end]
    child2_victims[start:end] = parent2['victims'][start:end]

    fill_positions = [i for i in range(size) if child1_victims[i] is None]
    fill_values = [v for v in parent2['victims'] if v not in child1_victims]
    for pos, val in zip(fill_positions, fill_values):
        child1_victims[pos] = val

    fill_positions = [i for i in range(size) if child2_victims[i] is None]
    fill_values = [v for v in parent1['victims'] if v not in child2_victims]
    for pos, val in zip(fill_positions, fill_values):
        child2_victims[pos] = val

    return {'id': random.randint(0, 1e6), 'victims': child1_victims}, \
        {'id': random.randint(0, 1e6), 'victims': child2_victims}

def crossover_population(population, total):
    offspring = []

    while len(offspring) < total:
        parent1, parent2 = random.sample(population, 2)

        child1, child2 = order_crossover(parent1, parent2)

        offspring.append(child1)
        offspring.append(child2)

    return offspring[:total]


def print_ids(population):
    log(' '.join([str(p['id']) for p in population]))


def log(msg):
    print(f"[{datetime.now()}] {msg}")

pop = None
for i in range(GENERATIONS):
    if i % 10 == 0:
        log(f"Running generation {i}")
    pop = run_gen(i, pop)
