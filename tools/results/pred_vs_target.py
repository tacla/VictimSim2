### VictimSim2: Predicted vs Target 
### Author: Cesar A. Tacla, UTFPR
###
## Compara as predições das classes de gravidade e da referência (target), no caso de um classificador.
## No caso de um regressor, compara as predições dos valores de gravidade das vítimas contra os
## valores de referência (target).
##
## Os arquivos a serem comparados são: 
##    file_target: arquivo com os resultados de referência
##    file_predict: arquivo com os resultados preditos
##
##    formato dos dois arquivos: CSV sem cabeçalho 
##    id, x, y, gravity, class
##
## Os arquivos target e de predição podem ter tamanhos diferentes: o da predição pode
## ser menor do que o de referência. Os casamentos são feitos por igualdade de <id> das vítimas.
##
## Resultados são calculados somente para casamentos perfeitos entre target e predito.

import csv
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score, mean_squared_error

# Input CSV file names
file_target = 'target.txt'
file_predict = 'pred.txt'
target_len = 0
predict_len = 0

# Initialize empty lists for the actual values and predicted values
actual_values = []
predicted_values = []
actual_labels = []
predicted_labels = []

# Initialize counter of found victims per label and summation of gravity 
grav_count=[0]*4
grav_sum=[0.0]*4
actual_grav_count=[0]*4
actual_grav_sum=[0.0]*4

# Read the secont-to-last column and columns 1, 2, and 3 of file_target and file_predict
with open(file_target, 'r') as target_file, open(file_predict, 'r') as predict_file:
    target_reader = csv.reader(target_file)
    predict_reader = csv.reader(predict_file)

    # Create a dictionary to store the gravity value and the gravity label of 
    # file_target based on column 1 (id))
    
    target_dict = {}

    for target_row in target_reader:
        key = target_row[0]                 # <id>
        grav_value = float(target_row[-2])  # before last column: gravity value
        grav_label = int(target_row[-1])    # Last column (integer): gravity label
        target_dict[key] = (grav_value, grav_label)
        actual_grav_sum[grav_label-1] += grav_value
        actual_grav_count[grav_label-1] += 1
        target_len += 1

    # Iterate through file_predict and compare with file_target
    for predict_row in predict_reader:
        key = predict_row[0]  # only id of the victim
        predict_len += 1

        if key in target_dict:
            # Matching row found in file_target
            grav_value, grav_label= target_dict[key]  # Get the gravity and the gravity label

            # Gravity label
            actual_labels.append(grav_label)
            grav_count[grav_label-1] += 1
            predicted_label = int(predict_row[-1])
            predicted_labels.append(predicted_label)

            # Gravity value
            actual_values.append(grav_value)
            grav_sum[grav_label-1] += grav_value
            predicted_value = float(predict_row[-2])  # Before last column
            predicted_values.append(predicted_value)

print(f"{'-'*60}")
print(f"GENERAL METRICS\n")
print(f"Reference dataset: {file_target} Length: {target_len}")
print(f"Predict          : {file_predict} Length: {predict_len}")
print(f"Matching rows    : {len(predicted_values)}")
print("")

print(f"{'-'*60}")
print(f"REGRESSOR METRICS")
# Calculate RMSE
rmse = np.sqrt(mean_squared_error(actual_values, predicted_values))

# Print the RMSE
print(f"Root Mean Square Error (RMSE) for matching rows: {rmse:.2f}")
print("")

print(f"{'-'*60}")
print(f"CLASSIFICATION METRICS")

# Print the last value confusion matrix, precision, recall, F1-score, and accuracy
conf_matrix = confusion_matrix(actual_labels, predicted_labels, labels=[1,2,3,4])
accuracy = accuracy_score(actual_labels, predicted_labels)
class_report = classification_report(actual_labels, predicted_labels, labels=[1,2,3,4], target_names=['Critico', 'Instavel', 'Pot Estavel', 'Estavel'], zero_division=0)

print("\nConfusion Matrix:")
print(conf_matrix)
print("\nAccuracy:", accuracy)
print("\nClassification Report:")
print(class_report)
print("")

print(f"{'-'*60}")
print(f"SPECIFIC METRICS\n")

print(f"   Critical victims   (1) = {grav_count[0]:3d} out of {actual_grav_count[0]} ({100*grav_count[0]/actual_grav_count[0]:.1f})%")
print(f"   Instable victims   (2) = {grav_count[1]:3d} out of {actual_grav_count[1]} ({100*grav_count[1]/actual_grav_count[1]:.1f})%")
print(f"   Pot. inst. victims (3) = {grav_count[2]:3d} out of {actual_grav_count[2]} ({100*grav_count[2]/actual_grav_count[2]:.1f})%")
print(f"   Stable victims     (4) = {grav_count[3]:3d} out of {actual_grav_count[3]} ({100*grav_count[3]/actual_grav_count[3]:.1f})%")
print(f"   --------------------------------------")
print(f"   Total of victims  = {len(predicted_values):3d} ({100*float(len(predicted_values)/target_len):.2f}%)")

weighted = ((6*grav_sum[0] + 3*grav_sum[1] + 2*grav_sum[2] + grav_sum[3])/
(6*grav_count[0] + 3*grav_count[1] + 2*grav_count[2] + grav_count[3]))

print("")
print(f"   Weighted victims per severity = {weighted:.2f}\n")

tot_grav_sum = sum(grav_sum)
tot_actual_grav_sum = sum(actual_grav_sum)
print(f"   Sum of gravities of matched victims = {tot_grav_sum:.2f} of a total of {tot_actual_grav_sum:.2f}")
print(f"     % of gravities of matched victims = {tot_grav_sum/tot_actual_grav_sum:.2f}")

