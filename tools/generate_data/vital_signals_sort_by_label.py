import csv

def sort_csv_by_last_column(input_file, output_file):
    """Sorts a CSV env_vital_signals.txt file by the last column (severity label) in descending order
    Args:
        input_file: The name of the input CSV file.
        output_file: The name of the output CSV file.
    """

    with open(input_file, 'r', newline='') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # Read all rows into a list
        rows = list(reader)

        # Sort the rows by the last column in descending order, ignoring spaces after the comma
        def key_func(row):
            last_column = row[-1].strip()  # Remove leading and trailing spaces
            return int(last_column)
        rows.sort(key=key_func, reverse=True)

        # Write the sorted rows to the output file
        writer.writerows(rows)

if __name__ == '__main__':
    input_file = 'env_vital_signals.txt'
    output_file = 'env_vital_signals_sorted.txt'
    sort_csv_by_last_column(input_file, output_file)
