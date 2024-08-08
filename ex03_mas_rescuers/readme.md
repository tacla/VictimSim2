# Example of a Multiagent system
This system has 4 explorer agents running depth-first search for exploring the environment and 4 rescuer agents with placeholders for the following functions:
* **Clustering**: a naive one, based on grouping the found victims according to their quadrants
* **Sequencing of rescue**: it orders the victims by x coordinates followed by the y coordinates, both in ascending order
* **Assigning clusters** to the rescuers: it trivially assigns 1 cluster to each rescuer
* **Breadth-first search** for calculating the paths for rescuing the victims: it departs from the base, goes to each victim, and comes back to the base (it does not control the consumed battery time)

One of the rescuer agents is the master rescuer. It is in charge of synchronizing the explorers at the end of exploration phase. The master collects all the partial maps, unifies them, as well as the data about the found victims. Follow, it instantiates three more rescuer agents all having the same unified map and data about victims.

To run, reproduce the below structure of folders and files:

* `clusters`      *this folder stores the clusters and sequences of rescue*
  * cluster1.txt
  * ...
  * cluster4.txt
  * seq1.txt
  * ...
  * seq4.txt
* `cfg_1`        *this folder stores the configuration files of all agents*
  * explorer_1_config.txt 
  * ... 
  * explorer_4_config.txt
  * rescuer_1_config.txt
  * ...
  * rescuer_4_config.txt
* `vs`
  * all  .py of the vs folder
* bfs.py
* explorer.py
* **main.py**       *this is the file to be executed, in there you should configure the paths for the datasets and config files*
* map.py
* rescuer.py
