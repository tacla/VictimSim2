## Generate a dataset containing the difficulty of access to each victim. Each row is composed of::
## - the difficulty of access, a float value explained below.
## - the Euclidian distance of the victim to the base: victim's (x, y) coming from the env_victims.txt to the (xb, yb)
## - the sev_value: the severity of injury of a victim, a float value coming from the env_vital_signals.txt
##
## This dataset should be completed, for instance, with a class label to be used in supervised learning
## representing jointly the difficulty of access and the injury severity. 
## It may be useful for ordering the victims' rescue.
##
##  Input: env_victims.txt and env_vital_signals.txt (same number of victims), and env_obst.txt
##  Output: difficulty.txt (the generated dataset)
##
##  You have to set these variables before running:
##  - xmax, ymax: the upper indexes for x and y
##  - xb, yb: the base coordinates

import csv
import math

# Define max value for x and y axis (including the limits)
# For a 12 x 12 grid, you should put xmax=11 and ymax=11 considering that it starts at (0,0)
xmax = 89
ymax = 89

# Define the base coordinates
xb, yb = 4, 60

# Function to calculate euclidean distance between two points
def euclidean_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Function to get difficulty level of access for a given position
def get_difficulty(x, y, obstacles):
    difficulty = 0
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            nx, ny = x + dx, y + dy
            if 0 <= nx <= xmax and 0 <= ny <= ymax:
                obstacle_row = next((row for row in obstacles if row[0] == nx and row[1] == ny), None)
                print(f"({x} {y}): {obstacle_row}")
                if obstacle_row:
                    difficulty += obstacle_row[2]
                else:
                    difficulty += 1
            else:
                difficulty += 100.0
                
    return difficulty



# Read env_obsts.txt
obstacles = []
with open('env_obst.txt', 'r') as obst_file:
    obst_reader = csv.reader(obst_file)
    for row in obst_reader:
        obstacles.append([int(row[0]), int(row[1]), float(row[2])])

# Open output CSV file
with open('difficulty.txt', 'w', newline='') as output_file:
    writer = csv.writer(output_file)

    # Write header
    writer.writerow(['diff', 'dist', 'sev'])

    # Read env_victims.txt and env_vital_signals.txt simultaneously
    with open('env_victims.txt', 'r') as victims_file, open('env_vital_signals.txt', 'r') as signals_file:
        victims_reader = csv.reader(victims_file)
       
        signals_reader = csv.reader(signals_file)

        for victim_row, signal_row in zip(victims_reader, signals_reader):
            # Extract victim coordinates
            print(f"victim: {victim_row}")
            print(f"vital signals: {signal_row[0]} {signal_row[6]}")
            x, y = int(victim_row[0]), int(victim_row[1])

            # Calculate distance to base
            distance_to_base = euclidean_distance(x, y, xb, yb)
            print(f"distance: {distance_to_base:.2f}\n")

            # Extract sev_value
            sev_value = float(signal_row[6])

            # Calculate difficulty of access
            difficulty = get_difficulty(x, y, obstacles)

            # Write to output CSV
            writer.writerow([difficulty, distance_to_base, sev_value])

print("Output CSV file generated successfully.")
