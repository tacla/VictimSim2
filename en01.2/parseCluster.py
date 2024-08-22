import csv
import ast

for i in range(1, 5):
    order_mapping = {}
    with open(f'./cluster{i}/cluster{i}-population-gen1000.csv', mode='r') as order_file:
        order_reader = csv.DictReader(order_file)
        for row in order_reader:
            victims = list(map(int, row['victims'].split()))
            for index, victim_id in enumerate(victims):
                order_mapping[victim_id] = index

    data = []
    with open(f'./cluster{i}.csv', mode='r') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            victim_id = int(row['ID'])
            coordinates = ast.literal_eval(row['Coordenadas'])
            x = int(coordinates[0])
            y = int(coordinates[1])
            if victim_id in order_mapping:
                data.append((order_mapping[victim_id], victim_id, x, y, 0.5, 3))

    data.sort()

    with open(f'cluster{i}-p.csv', mode='w', newline='') as outfile:
        writer = csv.writer(outfile)
        for _, victim_id, x, y, g, z in data:
            writer.writerow([victim_id, x, y, g, z])