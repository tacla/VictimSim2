##################################
## Author: Cesar Tacla, UTFPR
##
## Read the env_vital_signals.txt, a CSV file with the victims' vital signals
## and renumber all the victims' ids starting from zero.
##
## Also, print the number of victims and their severity values per category
## 1 - critical, 2 - unstable, 3 - potentially stable, 4 - stable
##
import csv
import os

# Define the input file name
input_file = 'env_vital_signals.txt'
output_file = 'env_vital_signals_temp.txt'

# Initialize the sequential number starting from zero
sequential_number = 0
line_count = 0  # Variable to count the number of lines

# Initialize vectors for severity counts, accumulated severity values, and severity labels
severity_counts = [0, 0, 0, 0]  # For severity labels 1, 2, 3, and 4
accumulated_severity = [0.0, 0.0, 0.0, 0.0]  # Accumulated severity values for labels 1, 2, 3, and 4
severity_labels = ["critical     ", "unstable     ", "pot. unstable", "stable       "]

# Open the input file and create a temporary output file
with open(input_file, mode='r', newline='') as infile, open(output_file, mode='w', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    # Read each row, replace the first field, and write to the output file
    for row in reader:
        # Replace the first field with the sequential number
        row[0] = sequential_number
        sequential_number += 1
        
        # Get the severity label (last column) and severity value (before-last column)
        sev_label = int(row[-1])
        severity_value = float(row[-2])

        # Update the count and accumulated severity based on the severity label
        if 1 <= sev_label <= 4:
            index = sev_label - 1  # Map severity label (1, 2, 3, 4) to vector indices (0, 1, 2, 3)
            severity_counts[index] += 1
            accumulated_severity[index] += severity_value
        
        # Write the modified row to the output file
        writer.writerow(row)
        
        line_count += 1  # Increment the line count

# Replace the original file with the modified file
os.replace(output_file, input_file)

# Calculate total accumulated severity value
total_accumulated_severity = sum(accumulated_severity)

# Print the total number of lines processed
print(f"The victim IDs in {input_file} have been replaced with sequential numbers starting from zero.")
print(f"Total number of lines processed: {line_count}")

# Print the severity counts, accumulated severity values, and their percentages
print("\nSeverity label counts, accumulated severity values, and percentages:")
for i in range(4):
    count_percentage = (severity_counts[i] / line_count) * 100 if line_count > 0 else 0
    severity_percentage = (accumulated_severity[i] / total_accumulated_severity) * 100 if total_accumulated_severity > 0 else 0
    print(f"{i+1} {severity_labels[i]}:\t{severity_counts[i]} ({count_percentage:.2f}%)\tSev. value: {accumulated_severity[i]:.3f} ({severity_percentage:.2f})%")


# Print the total numbers for the severity labels and severity values
print("\nTotal numbers:")
print(f"Nb of victims: {sum(severity_counts)}")
print(f"Accumulated Severity Value: {total_accumulated_severity}")
