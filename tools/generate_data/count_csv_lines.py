## Counts the number of lines of every *.txt file in the current directory

import os

def count_lines_in_file(file_path):
    with open(file_path, 'r') as file:
        line_count = sum(1 for line in file)
    return line_count

if __name__ == "__main__":
    current_directory = os.getcwd()
    
    for file_name in os.listdir(current_directory):
        if file_name.endswith('.txt'):
            file_path = os.path.join(current_directory, file_name)
            try:
                num_lines = count_lines_in_file(file_path)
                print(f"{file_name}: {num_lines} lines")
            except Exception as e:
                print(f"An error occurred while processing {file_name}: {e}")
