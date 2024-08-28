import csv
import random

def shuffle_csv(input_file, output_file):
    """Shuffles the rows of the env_vital_signals.txt file.

    Args:
        input_file: The name of the input CSV file.
        output_file: The name of the output CSV file.
    """

    with open(input_file, 'r', newline='') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # Read all rows into a list
        rows = list(reader)

        # Shuffle the rows randomly
        random.shuffle(rows)

        # Write the shuffled rows to the output file
        writer.writerows(rows)

if __name__ == '__main__':
    input_file = 'env_vital_signals_Q3.txt'
    output_file = 'env_vital_signals_Q3_shuffled.txt'
    shuffle_csv(input_file, output_file)
