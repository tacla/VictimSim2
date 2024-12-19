This folder contains python programs to show results, the grid, ...

exp_plot_results
----------------
>   Plot results of an experiment containing several runs of VictimSim2.  For each run, the VictimSim2 prints the number of found and saved victims . The user should copy and past these values to a CSV file. From this input file, the program plots histograms of saved/rescued victims per severity  (absolute values and relative to the total number of victims), and the Veg and Vsg metrics.


Create a CSV file, the descriptor of the dataset containing just one line for the header and the other, for the total number of victims per severity state (SG is the sum of the severity values of all victims)
```
     V1, V2, V3, V4, SG
     <nb. of V1>,<nb. of V2>, <nb. of V3>, <nb. of V4>, <sum of gravities>
```

Look for the following lines after excution completion:
 
 *** SAVED victims by all rescuer agents ***
```
     CSV of found victims
     Ve1,Ve2,Ve3,Ve4,Veg
     24,29,9,32,0.21615384615384614     CSV of found victims
```
and
```
     CSV of saved victims
     Vs1,Vs2,Vs3,Vs4,Vsg
     20,28,7,27,0.18846153846153846
```
For each run, copy and paste the values into a CSV file like this:
```
Ve1,Ve2,Ve3,Ve4,Veg,Vs1,Vs2,Vs3,Vs4,Vsg
24,29,9,32,0.21615384615384614,20,28,7,27,0.18846153846153846
...
```
After collecting the desired data, run the exp_plot_results.py
