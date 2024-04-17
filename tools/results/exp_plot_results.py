## exp_plot_results
## Auhor: Cesar A. Tacla, UTFPR
##
## Plot results of an experiment containing several runs of VictimSim2.
## For each run, the VictimSim2 saves the number of found and saved victims.
## From this, the program plots histograms of saved/rescued victims per severity
## (absolute values and relative to the total number of victims), and the Veg and Vsg
## metrics.
##
## Input: descriptor file and results file. You can get the values for these
##        files in the environmenta's stats printed at the end of execution.
##
## Output: graphics showing the mean value of saved and found victims after
##         several experiments. Graphics show the values per degree of severity.
##         Also, there is a graphic showing the Veg and Vsg metrics.
##
## descriptor file: one row for the header and just one row containing the
##                  total number of victims per severity and sum of severity
##                  values for all victims
##                 V1,V2,V3,V4,SG    # HEADER
##                <V1,V2,V3,V4,SG>   # VALUES
##
## results file: one row for the header and one row per each run
##                |- found victims -| |- saved victims -|
##                Ve1,Ve2,Ve3,Ve4,Veg,Vs1,Vs2,Vs3,Vs4,Vsg   # HEADER
##               <Ve1,Ve2,Ve3,Ve4,Veg,Vs1,Vs2,Vs3,Vs4,Vsg>  # VALUES for a run

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math

descriptor_file = 'exp_300v_90x90_descriptor.txt'
results_file = 'exp_300v_90x90_results.txt'

# Read the CSV file containing descriptors into a pandas DataFrame
df_descriptor = pd.read_csv(descriptor_file, skipinitialspace=True)
nb_of_victims = df_descriptor.iloc[0].tolist()
print(f"Descriptor")
print(f"{df_descriptor}")

# Read the CSV file into a pandas DataFrame
df = pd.read_csv(results_file, skipinitialspace=True)
print()
print(f"Data")
print(df)
print(f"Runs: {len(df)}")

# Separate columns starting with 'Ve' and 'Vs'
ve_columns = [col for col in df.columns if col.startswith('Ve') and col != 'Veg']
vs_columns = [col for col in df.columns if col.startswith('Vs') and col != 'Vsg']

# Calculate mean and standard deviation for 'Ve' columns (absolute values)
ve_means = df[ve_columns].mean()
ve_std = df[ve_columns].std()

# Calculate mean and standard deviation for 'Vs' columns (absolute values)
vs_means = df[vs_columns].mean()
vs_std = df[vs_columns].std()

# Calculate mean and standard deviation for 'Veg' and 'Vsg' columns
veg_mean = df['Veg'].mean()
veg_std = df['Veg'].std()

vsg_mean = df['Vsg'].mean()
vsg_std = df['Vsg'].std()

max_mean = math.ceil(max(ve_means.max(), vs_means.max()))
print(f"Max mean value: {max_mean}")
                     
# Dictionary to store relative mean and standard deviation for each column of found victims
rel_ve = {}

# Calculate relative mean and standard deviation for each column of found victims
i = 0
for col in ve_columns:
    rel_col = df[col] / nb_of_victims[i]
    rel_ve[col] = {'mean': rel_col.mean(), 'std_dev': rel_col.std()}
    i += 1

# Dictionary to store relative mean and standard deviation for each column of saved victims
rel_vs = {}

# Calculate relative mean and standard deviation for each column of saved victims
i = 0
for col in vs_columns:
    rel_col = df[col] / nb_of_victims[i]
    rel_vs[col] = {'mean': rel_col.mean(), 'std_dev': rel_col.std()}
    i += 1

# Plotting
fig, axes = plt.subplots(3, 2, figsize=(12, 8))
axes= axes.ravel()

# Plot for Ve columns
axes[0].bar(ve_means.index, ve_means, yerr=ve_std, capsize=5, color='blue', alpha=0.7)
axes[0].set_title('Mean number of found victims per severity (abs)')
axes[0].set_ylim(0, max_mean)
axes[0].set_ylabel('Nb of victims')

print(f"\nFound victims (mean abs value)")
print(f"{ve_means.to_string(index=True, header=True)}")

# Plot for relative values of Ve (found)
rel_means = [value['mean'] for value in rel_ve.values()]
rel_std_dev = [value['std_dev'] for value in rel_ve.values()]
axes[1].bar(ve_means.index, rel_means, yerr=rel_std_dev, capsize=5, color='blue', alpha=0.7)
axes[1].set_title('Mean number of found victims per severity (%)')
axes[1].set_ylim(0, 1)
axes[1].set_ylabel('Nb of victims(%)')

print(f"\nFound victims (mean value over the total of victims)")
for i in range(len(rel_means)):    
    print(f"Ve{i+1:1d}: {rel_means[i]:.4f}%")

# Plot for 'Vs' columns
axes[2].bar(vs_means.index, vs_means, yerr=vs_std, capsize=5, color='green', alpha=0.7)
axes[2].set_title('Mean number of saved per severity (abs)')
axes[2].set_ylim(0, max_mean)
axes[2].set_ylabel('Nb of victims')

print(f"\nSaved victims (mean abs value)")
print(f"{vs_means.to_string(index=True, header=True)}")

# Plot for relative values of Vs (saved)
rel_means = [value['mean'] for value in rel_vs.values()]
rel_std_dev = [value['std_dev'] for value in rel_vs.values()]
axes[3].bar(vs_means.index, rel_means, yerr=rel_std_dev, capsize=5, color='green', alpha=0.7)
axes[3].set_title('Mean number of saved victims per severity (%)')
axes[3].set_ylim(0, 1)
axes[3].set_ylabel('Nb of victims (%)')

print(f"\nSaved victims (mean value over the total of victims)")
for i in range(len(rel_means)):    
    print(f"Vs{i+1:1d}: {rel_means[i]:.4f}%")

### Plot for 'Veg' and 'Vsg' columns
veg_vsg_means = [veg_mean, vsg_mean]
veg_vsg_std = [veg_std, vsg_std]
axes[4].bar(['Veg', 'Vsg'], veg_vsg_means, yerr=veg_vsg_std, capsize=5, color='orange', alpha=0.7)
print(f"\nVeg and Vsg")
print(f"Veg: {veg_mean:.3f}")
print(f"Vsg: {vsg_mean:.3f}")

### Plot the source of data
axes[5].axis('off')
axes[5].text(0.05,0.75, results_file, ha="left", fontsize=10, transform=axes[5].transAxes)
axes[5].text(0.05,0.50, df_descriptor.to_string(index=False, header=True), fontsize=10, transform=axes[5].transAxes)
axes[5].text(0.05,0.25, f"Nb.of runs {len(df)}", fontsize=10, transform=axes[5].transAxes)

plt.subplots_adjust(hspace=0.5)  # Adjust spacing between subplots
plt.tight_layout(pad=3.0)
plt.show()
