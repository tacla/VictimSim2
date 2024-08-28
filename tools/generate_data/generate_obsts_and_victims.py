## Author: Tacla, UTFPR, 2024
##
## Generate obstacles reading a input file with the following format per line:
## <x_ini>, <y_ini>, <x_end>, <y_end>, <difficulty of access> 
##
## It works for hor, ver and diag lines.
##
## Besides, if you define N_VICTIMS > 0, the program generates N_VICTIMS
## situated in random positions (except at coordinates where there is a wall).
##
## Outputs:
## - obst_file: contains the list of cells containing the obstacles with their difficulties of access.
## - victims_file: a list of N_VICTIMS with random generated coordinates
##
## To show the grid, use the plot_2d_grid.py

import random

## To be configured
input_file = "input.txt"         #input
obst_file = "env_obst.txt"      #out
victims_file = "env_victims.txt" #out

X_MIN = 0    # Minimum value for x index (including it)
X_MAX = 22   # maximum value for x index (including it)
Y_MIN = 0    # the same for y
Y_MAX = 22                     
N_VICTIMS = 59  # n random coordinates 

######

with open(input_file, "r") as f:
    obst_raw = f.readlines()
    obst = {}   # a dictionary: key (col, row): difficulty
    for row in obst_raw:
        data = row.split(',')
        data = [item.strip() for item in data]   # remove spaces
        coord = [int(item) for item in data[:4]] # [col1,row1,col2,row2]
        diff = float(data[4])
        
        if coord[1] == coord[3]:
            # horizontal obstacle
            for c in range(coord[0], coord[2]+1):
                key = (c, coord[1])
                obst[key] = diff
        elif coord[0] == coord[2]:
            # vertical obstacle
            for r in range(coord[1], coord[3]+1):
                key = (coord[0], r)
                obst[key] = diff
        else:
            # diagonal obstacle
            slope = (coord[3]-coord[1]) / (coord[2]-coord[0])
            if slope > 0:
                for c in range(coord[0], coord[2]+1):
                    r = coord[1] + int(round(slope*(c-coord[0])))
                    key=(c, r)
                    obst[key] = diff
            else:
                for c in range(coord[0], coord[2]+1):
                    r = r2 + int(round(slope*(c-coord[2])))
                    key=(c, r)
                    obst[key] = diff




with open(obst_file, "w") as f:
    for coord, diff in obst.items():
        f.write(f"{coord[0]},{coord[1]},{diff}\n")

# Generate N random points that do not coincide with any of the wall coordinates or any previously generated points
points = []
while len(points) < N_VICTIMS:
    x = random.randint(X_MIN, X_MAX)
    y = random.randint(Y_MIN, Y_MAX)

    if obst.get((x, y)) is None and (x, y) not in points:
        points.append((x, y))

if N_VICTIMS > 0:
    # Sort the points by row number and then by column number
    points = sorted(points, key=lambda x: (x[0], x[1]))

    # Write the points to the output file, one point per line in the format row, column
    with open(victims_file, "w") as f:
        for point in points:
            f.write(f"{point[0]},{point[1]}\n")
