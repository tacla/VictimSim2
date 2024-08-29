#############################################################################
## Cria o arquivo target para teste cego a partir dos arquivos:
## 1) env_vital_signals.txt
## 2) env_victims.txt
##
## Lê o arquivo de sinais vitais com valores e label de gravidade, o arquivo
## de coordenadas x, y das vítimas no ambiente e grava um arquivo de saida
## no formato: <id, x, y, gravidade, classe>

import csv

# Input CSV file names
file_vs = 'env_vital_signals.txt'
file_vict = 'env_victims.txt'

# Output CSV file name
file_verif = 'target.txt'

# Open file_vs and file_vict for reading
with open(file_vs, 'r') as vs_file, open(file_vict, 'r') as vict_file:
    # Create CSV readers for file_vs and file_vict
    vs_reader = csv.reader(vs_file)
    vict_reader = csv.reader(vict_file)

    # Open file_verif for writing
    with open(file_verif, 'w', newline='') as verif_file:
        # Create a CSV writer for file_verif
        verif_writer = csv.writer(verif_file)

        # Iterate through rows of file_vs and file_vict
        for vs_row, vict_row in zip(vs_reader, vict_reader):
            # Extract the desired columns
            id, grav, classe = vs_row[0], vs_row[6], vs_row[7]
            x, y = vict_row[0], vict_row[1]

            # Create a new row for file_verif
            verif_row = [id, x, y, grav, classe]

            # Write the row to file_verif
            verif_writer.writerow(verif_row)

print(f'File "{file_verif}" has been generated.')
