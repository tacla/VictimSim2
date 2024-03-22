## VictimSim2
## Author: Cesar Tacla, UTFPR
##
## It transformas a env_walls.txt config file into the new one: env_obsts.txt
##   (from the version 1's format to the version 2)
## - it adds a third column to every line of the walls with the value VS.OBST_WALLS (100)
## - it adds K new obstacles within the range [max_width, max_height] given as arguments
## - each new obstacle has a degree of difficulty in the range [min_difficulty, max_difficulty]
##   given as arguments
## e.g. transf_walls_to_vs2(7, 20, 24, 0.5, 3)
##       K=7
##       max_width = 20       max_height= 24
##       min_difficuly = 0.5  max_difficulty = 3
##
## The default input file is env_walls.txt and the output file is env_obst.txt

import csv
import random
import argparse

def add_difficulty_column(input_file,output_file):
    with open(input_file, 'r') as f_read, open(output_file, 'w', newline='') as f_write:
        reader = csv.reader(f_read)
        writer = csv.writer(f_write)
        
        for row in reader:
            writer.writerow(row + ['100'])  # 100 eh o valor de um obstaculo intrasnponivel (parede)
    return output_file

def check_duplicates(coords, new_coord):
    for coord in coords:
        if coord[0] == new_coord[0] and coord[1] == new_coord[1]:
            return True
    return False

def generate_obstacles(output_file, k, max_width, max_height, min_difficulty, max_difficulty):
    existing_coords = []
    with open(output_file, 'r') as f_read:
        reader = csv.reader(f_read)
        for row in reader:
            existing_coords.append((int(row[0]), int(row[1])))
                
    with open(output_file, 'a', newline='') as f_write:
        writer = csv.writer(f_write)
        
        for _ in range(k):
            new_coord = (random.randint(0, max_width - 1), random.randint(0, max_height - 1))
            while check_duplicates(existing_coords, new_coord):
                new_coord = (random.randint(0, max_width - 1), random.randint(0, max_height - 1))
                
            existing_coords.append(new_coord)
            # difficulty com uma casa decima apenas
            difficulty =  random.randint(int(10 * min_difficulty), int(10 * max_difficulty))/10
            writer.writerow([new_coord[0], new_coord[1], difficulty])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate environment obstacles")
    parser.add_argument("k", type=int, help="Number of new obstacles")
    parser.add_argument("max_width", type=int, help="Maximum width")
    parser.add_argument("max_height", type=int, help="Maximum height")
    parser.add_argument("min_difficulty", type=float, help="Minimum difficulty")
    parser.add_argument("max_difficulty", type=float, help="Maximum difficulty")
    args = parser.parse_args()

    input_file = "env_walls.txt"
    output_file = "env_obst.txt"
    output_file = add_difficulty_column(input_file, output_file)
    generate_obstacles(output_file, args.k, args.max_width, args.max_height, args.min_difficulty, args.max_difficulty)
    print("Obstacles generated and appended to the file:", output_file)
