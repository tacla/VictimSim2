# EXAMPLE 01: Manually controlled explorer and fixed rescue plan
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
      + abstract_agent.py
      + constants.py
      + environment.py
      + physical_agent.py

## Datasets ##
The datasets include information about the environment (such as size and obstacles) and the victims (including their positions and vital signs). To ensure other systems can also access and utilize these datasets, let's create a folder outside the multiagent system's scope.
- download the dataset containing [12 victims in a 12 x 12 grid](https://downgit.github.io/#/home?url=https://github.com/tacla/VictimSim2/tree/main/datasets/data_10v_12X12)
- extract all the files in the folder **[datasets]**. This last is at the same level of the **[target]** folder.

You should get a file structure like:
+ **[target]**
+ **[datasets]**
  + [data_10v_12X12]
    + env_config.txt          *environment configuration*
    + env_obst.txt            *obstacles' positions*
    + env_victims.txt         *victims' positions*
    + env_vital_signals.txt   *victims' vital signals*
   
## Run ##
Now, you can run the system from the *main.py*
