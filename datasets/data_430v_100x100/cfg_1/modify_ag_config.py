"""
This script processes agents' configuration files in a given folder. Each config file contains lines
formatted as PROPERTY VALUE, where:
- PROPERTY is a plain text identifier (no quotes)
- VALUE can be a string, a tuple, an integer, or a float

The script modifies, adds, or deletes PROPERTY-VALUE pairs in the files based on
a user-defined instruction dictionary.

Instruction format:
    {
        (operation, property): value
    }

Where:
- operation is one of:
    'i' → include (adds a new property if it does not exist)
    'r' → replace (modifies the value of an existing property)
    'd' → delete (removes the property if it exists)

The script processes all files in the target folder whose names start with a given prefix.

Example:
    If the prefix is 'resc' and the instruction is:
        {('i', 'TL'): 50}
    Then the line:
        TL 50
    will be added to all files whose names start with 'resc', unless TL already exists.

"""

import os

def process_files(folder, prefix, instructions):
    for filename in os.listdir(folder):
        if filename.startswith(prefix):
            path = os.path.join(folder, filename)
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Build current configuration dictionary
            config = {}
            for line in lines:
                if line.strip() == "":
                    continue
                parts = line.strip().split(maxsplit=1)
                if len(parts) == 2:
                    key, value = parts
                    config[key] = value

            # Apply instructions
            for (operation, key), value in instructions.items():
                if operation == 'i':  # inclusion
                    if key not in config:
                        config[key] = str(value)
                elif operation == 'r':  # replace
                    if key in config:
                        config[key] = str(value)
                elif operation == 'd':  # delete
                    config.pop(key, None)

            # Rewrite the file with updated content
            with open(path, 'w', encoding='utf-8') as f:
                for key, value in config.items():
                    f.write(f"{key} {value}\n")

            print(f"File '{filename}' processed.")

# === Example usage ===

# Path to the folder containing the files
folder = '.'

# Prefix to identify files to be processed
prefix = 'resc'

# Dictionary of instructions
# Format: (operation, property): value
instructions = {
    ('r', 'TLIM'): 1000,
}

process_files(folder, prefix, instructions)
