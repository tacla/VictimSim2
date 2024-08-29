###########################################################################
## Le o arquivo de sinais vitais e reescreve o valor de gravidade com zero
## e o label com 1 para que testes cegos possam ser feitos
##

import csv

def replace_columns(input_file, output_file):
    with open(input_file, 'r', newline='') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        replacements = 0
        for row in reader:
            row[-1] = 1
            row[-2] = 0.0
            writer.writerow(row)
            replacements += 1

    print(f"Replaced {replacements} values.")

### Main ###

input_file = "env_vital_signals.txt"
output_file = "env_vital_signals_cego.txt"
replace_columns(input_file, output_file)




     
            
