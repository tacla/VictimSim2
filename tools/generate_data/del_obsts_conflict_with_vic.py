## This program reads the file env_victims.txt and if the (x, y) victim's coordinate matches
## a wall (an obstacle with difficulty = 100.0), then it removes the wall.
##
## input: env_obst.txt and env_victims.txt
## output: filtered_env_obst.txt without walls that were in the same position as the victims


# Read env_obst.txt and store its contents in a list of tuples
with open('env_obst.txt', 'r') as obst_file:
    obst_data = [line.strip().split(',') for line in obst_file]

# Read env_victims.txt and store its contents in a list of tuples
with open('env_victims.txt', 'r') as victims_file:
    victims_data = [line.strip().split(',') for line in victims_file]

# Initialize a list to store filtered out rows
filtered_out_rows = []

# Filter out rows from obst_data where difficulty = 100.0 and the coordinates match with victims_data
filtered_obst_data = []
for row in obst_data:
    if float(row[2]) == 100.0 and (row[0], row[1]) in [(v[0], v[1]) for v in victims_data]:
        filtered_out_rows.append(row)
    else:
        filtered_obst_data.append(row)

# Print filtered out rows
print("Filtered out rows:")
for row in filtered_out_rows:
    print(','.join(row))

# Write filtered data to filtered_env_obst.txt
with open('filtered_env_obst.txt', 'w') as filtered_file:
    for row in filtered_obst_data:
        filtered_file.write(','.join(row) + '\n')
