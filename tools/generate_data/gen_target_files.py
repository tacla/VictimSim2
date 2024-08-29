"""
Extracts the before last and last columns from a CSV file and saves them to separate files.

Args:
   input_file (str): the env_vital_signals.txt file (with severity values and labels)
   file_values (str): the target file for the severity values
   file_labels (str): the target file for the severity labels
"""

import csv

def extract_target_values(input_file, out_values, out_labels):
    with open(input_file, 'r', newline='') as infile:
        reader = csv.reader(infile)

        with open(out_values, 'w', newline='') as sev_values_file, open(out_labels, 'w', newline='') as sev_labels_file:
            sev_values_writer = csv.writer(sev_values_file)
            sev_labels_writer = csv.writer(sev_labels_file)
            count = 0

            for row in reader:
                # Extract the before last and last columns
                sev_value = row[-2].lstrip()  # severity value
                sev_label = row[-1].lstrip()  # severity label
                
                # Write the values to the respective output files
                sev_values_writer.writerow([sev_value])
                sev_labels_writer.writerow([sev_label])
                count += 1

            print(f"{out_values} and {out_labels} generated with {count} rows each")

# Example usage
input_file = "env_vital_signals.txt"
file_values = "target_values.txt"
file_labels = "target_labels.txt"
extract_target_values(input_file, file_values, file_labels)
