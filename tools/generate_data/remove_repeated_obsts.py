## Reads the file env_obst.txt composed of three columns separated by commas:
## x, y, difficulty
## The program  keep only one row per x and y values containing
## the greater value of difficulty of access.

def read_file(filename):
    data = []
    with open(filename, 'r') as file:
        for line in file:
            x, y, diff = line.strip().split(',')
            data.append((int(x), int(y), float(diff)))
    return data

def filter_data(data):
    filtered_data = {}
    removed_rows = []
    for x, y, diff in data:
        diff_rounded = round(diff / 0.25) * 0.25  # Round diff to multiples of 0.25
        if (x, y) not in filtered_data or diff_rounded > filtered_data[(x, y)][2]:
            if (x, y) in filtered_data:
                removed_rows.append(filtered_data[(x, y)])
            filtered_data[(x, y)] = (x, y, diff_rounded)
        else:
            removed_rows.append((x, y, diff_rounded))
    return sorted(list(filtered_data.values()), key=lambda x: (x[0], x[1], x[2])), removed_rows

def write_file(filename, data):
    with open(filename, 'w') as file:
        for x, y, diff in data:
            file.write(f"{x},{y},{diff}\n")

def main():
    filename = 'env_obst.txt'
    filtered_filename = 'filtered_env_obst.txt'

    # Read data from file
    data = read_file(filename)

    # Filter data
    filtered_data, removed_rows = filter_data(data)

    # Write filtered data to a new file
    write_file(filtered_filename, filtered_data)

    print("Filtered data has been written to filtered_env_obst.txt")
    print("Removed rows:")
    for row in removed_rows:
        print(row)

if __name__ == "__main__":
    main()
