## Plot grid with walls, obstacles and victims' positions.
## Author: Cesar Tacla, 01 July 2025
##
## Read the obstacles file and the victims' coordinates file and plot the 2D grid.
##
## The 2D grid's origin is at the top left corner. Indexation is (column, row).
##
## This program prints the metrics per quadrant (victims and walls per quadrant)
##    upper left | upper right
##    -----------+------------
##    lower left | lower right
##
## To run this program you have to:
## - set the variables of the section Input files and parameters

import pygame
import os
import random
import math
import csv
import sys

# Input files and parameters - to be set
data_folder = "."
obst_file = "env_obst.txt"                        # the program concatenates data_folder + obst_file                      
victims_file = "env_victims.txt"                  # the program concatenates data_folder + victims_file
R = 100                                           # define the number of rows of the grid
C = 100                                           # define the number of columbs of the grid
WIDTH = 700                                       # define the window width in pixels
HEIGHT = 700                                      # define the window height in pixels

# initial settings
CELLW = WIDTH/C
CELLH = HEIGHT/R
base_c = 0
base_r = 0
base_coords = (base_c, base_r)

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YEL = (255, 255, 0)
GRAY = (100, 100, 100)
OBST_COLOR = (200, 255, 255)


def distance(p1, p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


# counters
vics_quad=[0]*4  # victims per quadrant
walls_quad=[0]*4 # walls per quadrant
tot_vics=0       # total of victims
tot_walls=0      # total of walls

        
# Create Pygame window
pygame.init()
font = pygame.font.Font(None, 24)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Grid')

# Fill background with white
screen.fill(WHITE)

# Draw grid cells as unfilled black rectangles
for r in range(R):
    for c in range(C):
        pygame.draw.rect(screen, (230,230,230), (c * CELLW, r * CELLH, CELLW, CELLH), 1)

print(f"\n----------------------------------------")
print(f"Total of rows......: {R}")
print(f"Total of cols......: {C}")
print(f"Total of cells.....: {R*C}")
print(f"Base position......: {base_coords}")

# Read wall coordinates from file
wall_coords = []
with open(os.path.join(data_folder, obst_file), 'r') as f:
    # Iterate over each line in the file
    for line in f:
        # Split the line by commas and convert each element to the appropriate type
        columns = line.strip().split(',')
        col1 = int(columns[0])
        col2 = int(columns[1])
        col3 = float(columns[2])
        
        # Check if the last column is equal to 100 = wall
        if col3 == 100.0:
            # Append the first two columns to the filtered_lines list
            wall_coords.append((col1, col2, BLACK))
        elif col3 > 0:
            obst_color = tuple(min(int(x/col3), 240) for x in OBST_COLOR)
            wall_coords.append((col1, col2, obst_color))

# Print the filtered lines
#print(wall_coords)
tot_walls = len(wall_coords)

# Read the victims' coordinates
vict_coords = []
with open(os.path.join(data_folder, victims_file), 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        x = int(row[0])
        y = int(row[1])
        vict_coords.append((x, y))   # append tuples

tot_vics = len(vict_coords)


# Plot the base position as a yellow rectangle
pygame.draw.rect(screen, YEL, (base_c * CELLW, base_r * CELLH, CELLW, CELLH))



# Plot walls as filled black rectangles and obstacles in a descending color scale (see OBST_COLOR)
for c, r, color in wall_coords:
    pygame.draw.rect(screen, color, (c * CELLW, r * CELLH, CELLW, CELLH))
    if r < R/2:
        if c < C/2:
            walls_quad[0] += 1
        else:
            walls_quad[1] += 1
    else:
        if c < C/2:
            walls_quad[2] += 1
        else:
            walls_quad[3] += 1

print(f"\n----------------------------------------")
gen_min_c = sys.maxsize
gen_min_r = sys.maxsize
gen_max_c = -sys.maxsize - 1
gen_max_r = -sys.maxsize - 1

#print(f"{gen_min_c}, {gen_min_r} : {gen_max_c}, {gen_max_r}")
mid_c = gen_min_c + (gen_max_c - gen_min_c)/2
#print(f"mid col {mid_c} = {mid_c * CELLW}")
mid_r = gen_min_r + (gen_max_r - gen_min_r)/2
pygame.draw.line(screen, (255,0,0), (mid_c * CELLW, gen_min_r * CELLH), (mid_c * CELLW, gen_max_r * CELLH), 2)
pygame.draw.line(screen, (255,0,0), (gen_min_c * CELLW, mid_r * CELLH), (gen_max_c * CELLW, mid_r * CELLH), 2)
pygame.draw.rect(screen, (255,0,0), (gen_min_c * CELLW, gen_min_r * CELLH, (gen_max_c - gen_min_c + 1) * CELLW, (gen_max_r - gen_min_r + 1) * CELLH), 2)


print(f"\n----------------------------------------")
print(f"Total of obstacles.....: {tot_walls} ({100*tot_walls/(R*C):.1f}% of the env)")
print(f"  upper left  quad.: {walls_quad[0]} ({100*walls_quad[0]/tot_walls:.1f}%)")
print(f"  upper right quad.: {walls_quad[1]} ({100*walls_quad[1]/tot_walls:.1f}%)")
print(f"  lower left  quad.: {walls_quad[2]} ({100*walls_quad[2]/tot_walls:.1f}%)")
print(f"  lower right quad.: {walls_quad[3]} ({100*walls_quad[3]/tot_walls:.1f}%)")

# Plot victims as circles
v = 0
color = RED
for c, r in vict_coords:
    v += 1
    pygame.draw.circle(screen, color, (c * CELLW + CELLW / 2, r * CELLH + CELLH / 2), 0.4*min(CELLW,CELLH))
    if r < R/2:
        if c < C/2:
            vics_quad[0] += 1
        else:
            vics_quad[1] += 1
    else:
        if c < C/2:
            vics_quad[2] += 1
        else:
            vics_quad[3] += 1

print(f"\n------------------------------------------") 
print(f"Total of victims...: {tot_vics}")
print(f"  upper left  quad.: {vics_quad[0]} ({100*vics_quad[0]/tot_vics:.1f}%)")
print(f"  upper right quad.: {vics_quad[1]} ({100*vics_quad[1]/tot_vics:.1f}%)")
print(f"  lower left  quad.: {vics_quad[2]} ({100*vics_quad[2]/tot_vics:.1f}%)")
print(f"  lower right quad.: {vics_quad[3]} ({100*vics_quad[3]/tot_vics:.1f}%)")



     


# Update Pygame display
pygame.display.update()

# Wait for user to close window
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:   ## left click
            # Get current mouse position
            x, y = event.pos
            # Convert mouse position to row and column indices
            r = int(y / CELLH)
            c = int(x / CELLW)
            # Draw row and column coordinates on screen
            font = pygame.font.SysFont('Arial', int(0.3*min(CELLW,CELLH)))
            text = font.render(f'({c},{r})', True, RED)
            text_rect = text.get_rect(center=(x, y))
            print(f'({c},{r})')
            screen.blit(text, text_rect)
            # Update Pygame display
            pygame.display.update()
