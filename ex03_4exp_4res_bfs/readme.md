# Example of a Multiagent system
This system has 4 explorer agents running depth-first search for exploring the environment and 4 rescuer agents with placeholders for the following functions:
* clustering (a naive one, based on quadrants)
* sequencing of rescue (it orders the victims by x coordinates in ascending order followed by the y coordinates)
* assigning clusters to the rescuers (trivially 1 cluster to each rescuer)
* breadth-first search for calculating the paths for rescuing the victims (departing from the base, passing by each victim)

One of the rescuer agents is the master rescuer. It is in charge of synchronizing the explorers at the end of exploration phase. The master collects all the partial maps, unifies them, as well as the data about the found victims.
