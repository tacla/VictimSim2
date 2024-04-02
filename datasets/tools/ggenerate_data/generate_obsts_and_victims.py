## Author: Tacla, UTFPR, 2024
##
## Generate obstacles reading a input file with the following format per line:
## col_ini,row_ini,col_end,row_end,difficulty of access 
##
## It calculates the cells building obstacles for horizontal, vertical and diagonal lines.
##
## Besides, if you define N_VICTIMS > 0, the program generates N_VICTIMS
## situated in random positions (except at coordinates where there is a wall).
## Also, you can include random obstacles in a grid region defining the constants
## concerning random obstacles
##
## Outputs:
## - obst_file: contains the list of cells containing the obstacles with their difficulties of access.
## - victims_file: a list of N_VICTIMS with random generated coordinates
##
## To show the grid, use the plot_2d_grid.py

import random

## To be configured
input_file = "input.txt"         #input
obst_file = "env_obst.txt"       #out
victims_file = "env_victims.txt" #out

MAX_ROWS = 90                    # grid size
MAX_COLS = 90
N_VICTIMS = 300                  # n random coordinates
N_VICTIMS_MAX_PER_REGION = 60    # puts the nb of victims in the random obstacles regions

# Random obstacles region
RND_OBST_COL_RANGES = [(0, 22), (70,89), (11, 45)]   # Pairwise with the row ranges, for instance, the first region
RND_OBST_ROW_RANGES = [(0, 21), (60,89), (45, 89)]   # is a rectangle from (0,0) to (22,22) in a (col, row) indexing
DIFF_RANGES=[(0.5, 3), (1.2, 2), (0.8, 1.5)]         # These are the difficulty ranges for each region

######

def calculate_cells(col1, row1, col2, row2):
    cells = [(col1, row1)]
    
    # Determine the direction of movement for each axis
    col_step = 1 if col2 > col1 else -1
    row_step = 1 if row2 > row1 else -1
    
    # Calculate the absolute differences in positions
    col_diff = abs(col2 - col1)
    row_diff = abs(row2 - row1)
    
    # Determine the direction of movement for diagonals
    col_diag_step = col_step if col_diff > 0 else 0
    row_diag_step = row_step if row_diff > 0 else 0
    
    # Determine the number of steps required for diagonal movement
    num_diag_steps = min(col_diff, row_diff)
    
    # Determine the remaining steps required for orthogonal movement
    num_ortho_steps_col = col_diff - num_diag_steps
    num_ortho_steps_row = row_diff - num_diag_steps
    
    # Add diagonal moves
    for i in range(1, num_diag_steps + 1):
        cells.append((col1 + i * col_diag_step, row1 + i * row_diag_step))
    
    # Add orthogonal moves
    for i in range(1, num_ortho_steps_col + 1):
        cells.append((col1 + num_diag_steps * col_diag_step + i * col_step, row1 + num_diag_steps * row_diag_step))
    for i in range(1, num_ortho_steps_row + 1):
        cells.append((col1 + num_diag_steps * col_diag_step, row1 + num_diag_steps * row_diag_step + i * row_step))
    
    return cells

with open(input_file, "r") as f:
    obst_raw = f.readlines()
    obst = {}   # a dictionary: key (col, row): difficulty
    for row in obst_raw:
        data = row.split(',')
        data = [item.strip() for item in data]   # remove spaces
        c1, r1, c2, r2 = [int(item) for item in data[:4]] # [col1,row1,col2,row2]
        diff = float(data[4])

        cells = calculate_cells(c1, r1, c2, r2)

        for cell in cells:
            obst[cell] = diff

vic_coords = []
for i in range(0, len(RND_OBST_COL_RANGES)):
    nb_of_victims = 0 # controle numero de vitimas por regiao
    for c in range(RND_OBST_COL_RANGES[i][0], RND_OBST_COL_RANGES[i][1]+1):
        for r in range(RND_OBST_ROW_RANGES[i][0], RND_OBST_ROW_RANGES[i][1]+1):
            if obst.get((c,r)) is None:
                obst[(c,r)] = random.uniform(DIFF_RANGES[i][0], DIFF_RANGES[i][1])
                if nb_of_victims < N_VICTIMS_MAX_PER_REGION and random.uniform(0,1) < 0.05:
                    vic_coords.append((c,r))
                    nb_of_victims += 1

with open(obst_file, "w") as f:
    for coord, diff in obst.items():
        f.write(f"{coord[0]},{coord[1]},{diff}\n")

# Generate the remaining victim coordinates
while len(vic_coords) < N_VICTIMS:
    c = random.randint(1, MAX_COLS-1)
    r = random.randint(1, MAX_ROWS-1)

    if obst.get((c, r)) is None and (c, r) not in vic_coords:
        vic_coords.append((c, r))

if N_VICTIMS > 0:
    # Sort the points by row number and then by column number
    vic_coords = sorted(vic_coords, key=lambda x: (x[0], x[1]))

    # Write the points to the output file, one point per line in the format row, column
    with open(victims_file, "w") as f:
        for coord in vic_coords:
            f.write(f"{coord[0]},{coord[1]}\n")
