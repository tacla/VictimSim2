# Example of a Multiagent system
This system has 4 explorer agents running depth-first search for exploring the environment and 4 rescuer agents with placeholders for the following functions:
* clustering (a naive one, based on quadrants)
* sequencing of rescue (it orders the victims by x coordinates in ascending order followed by the y coordinates)
* assigning clusters to the rescuers (trivially 1 cluster to each rescuer)
* breadth-first search for calculating the paths for rescuing the victims (from the base visiting each victim)
