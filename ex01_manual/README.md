# EXAMPLE 01: Manual controlled explorer and fixed rescue plan
This example allows the user to control the explorer agent with commands given by the keyboard. Upon reaching the time limit, the explorer agent calls the rescuer, which in turn executes a plan stored in memory.

How to use:
- download the **[ex01_manual]** folder (use [DownGit](https://downgit.github.io) or [direct here](https://downgit.github.io/#/home?url=https://github.com/tacla/VictimSim2/tree/main/ex01_manual))
- extract all the files in the selected **[target]** folder
  
- download the **[vs]** folder (use [DownGit](https://downgit.github.io) or [direct here](https://downgit.github.io/#/home?url=https://github.com/tacla/VictimSim2/tree/main/vs))
- extract all the files and copy the **[vs]** folder to the **[target]** folder

You should get a file structure like:

+ **[target]**
   + main.py
   + rescuer.py
   + explorer.py
   + **[vs]**
      + all the VictimSim .py

## Datasets ##
The datasets include information about the environment (such as size and obstacles) and the victims (including their positions and vital signs). To ensure other systems can also access and utilize these datasets, let's create a folder outside the multiagent system's scope.
