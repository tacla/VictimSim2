This folder contains the results obtained by running the random_dfs explorer and rescur agents with:
* dataset: 42v_20x20
* TLIM for the explorer: 600
* TLIM for the rescuer: 300

To see the results graphically, please run exp_plot_results.py available on the tools/visual

There are two files obtained from the prints of the environment.

exp_42v_20x20_descriptor.txt
----------------------------
Contains the descriptor of the victims file per severity
V1: nb of critical victims
V2: nb of instable
V3: nb of potentially instable
V4: nb of stable
SG: sum of the severity (gravidade) for all victims


exp_42v_20x20_results.txt
-------------------------
Contains the results of severalruns. Each line corresponds to one run.
Ve_i: found victims per severity
Veg : metric - nb of found victims weighted per severity
Vs_i: saved victims per severity
Vsg : metric - nb of saved victims weighted per severity

Graphics
--------
![Here](https://github.com/tacla/VictimSim2/blob/main/ex02_random_dfs/Results_42v_20x20/42v_20x20_results.png)
