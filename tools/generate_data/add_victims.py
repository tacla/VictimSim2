## Add N victims to the env_victims.txt within a square delimited
## by (x_min, y_min) to (x_max, y_max). See SETTING UP section.
## The coordinates of the victims are randomly generated to avoid
## coinciding with walls or other victims' coordinates.
##
## Input: env_obst.txt and env_victims.txt
## Output: new_env_victims.txt

import random

# SETTING UP
N = 3  # Number of new victims to generate
x_min, x_max = 15, 30  # Range of x values
y_min, y_max = 15, 30  # Range of y values
    
def read_file(filename):
    data = []
    with open(filename, 'r') as file:
        for line in file:
            if line.strip():  # Check if line is not empty
                data.append(line.strip().split(','))
    return data

##def write_file(filename, data):
##    with open(filename, 'w') as file:
##        for row in data:
##            file.write(','.join(row) + '\n')

def generate_victims(N, x_min, x_max, y_min, y_max, env_obst, env_victims):
    victims = []
    for _ in range(N):
        while True:
            x = random.randint(x_min, x_max)
            y = random.randint(y_min, y_max)
            if not any([obstacle[:2] == [x, y] and float(obstacle[2]) == 100.0 for obstacle in env_obst]) \
               and not any([victim == [str(x), str(y)] for victim in env_victims]):
                victims.append([str(x), str(y)])
                break
    return victims

def main():
    # Read env_obst.txt and new_env_victims.txt
    env_obst = read_file('env_obst.txt')
    env_victims = read_file('env_victims.txt')
    
    new_victims = generate_victims(N, x_min, x_max, y_min, y_max, env_obst, env_victims)
    print(f"{N} new victims added to new_env_victims.txt.")
    print("Newly created victims:")
    for victim in new_victims:
        print(','.join(victim))

    # make a copy of the env_victims.txt and add new generated victims
    with open('env_victims.txt', 'r') as env_victims_file:
        with open('new_env_victims.txt', 'w') as new_env_victims_file:
            # Read the content of the original file and write it to the copy file
            new_env_victims_file.write(env_victims_file.read())

            for victim in new_victims:
                new_env_victims_file.write(','.join(victim) + '\n')


if __name__ == "__main__":
    main()
