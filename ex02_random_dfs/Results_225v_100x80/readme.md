This folder contains the results obtained by running the random_dfs explorer and rescuer agents with:
* dataset: [`data_225v_100x80`](https://github.com/tacla/VictimSim2/tree/29e076897e4fe7c94887b74b2219d011882e701c/datasets/data_225v_100x80)
* TLIM for the explorer: 2000
* TLIM for the rescuer: 1000
* 1 explorer agent
* 1 rescuer agent

To see the results graphically, please run `exp_plot_results.py` available in the [`tools/visual/`](https://github.com/tacla/VictimSim2/tree/c36582490954ddb1b4d244c24addb30c9f43523b/tools/visual) folder. You will need both files available in the current folder for the program to run (see below). At the bottom of this page, you see the results.

exp_225v_100x80_descriptor.txt
----------------------------
Contains the descriptor of the victims file per severity
* V1: nb of critical victims
* V2: nb of instable
* V3: nb of potentially instable
* V4: nb of stable
* SG: sum of the severity (gravidade) for all victims


exp_225v_100x80_results.txt
-------------------------
Contains the results of several runs. Each line corresponds to one run.
* Ve<sub>i</sub>: found victims per severity
* Veg : metric - nb of found victims weighted per severity
* Vs<sub>i</sub>: saved victims per severity
* Vsg : metric - nb of saved victims weighted per severity

Graphics
--------
![Here](https://github.com/tacla/VictimSim2/blob/main/ex02_random_dfs/Results_225v_100x80/exp_225v_100x80_results.png)
