# EXAMPLE 02: Random explorer and a DFS rescuer
This example features an explorer agent that walks randomly in the environment. It constructs a map of the explored region containing the obstacles and victims. The explorer then passes the map to the rescuer. Subsequently, the rescuer walks using the depth-first search within the discovered region, attempting to rescue the found victims.

How to use:
- copy the explorer.py, rescuer.py, and main.py to some folder
- all the accessory .py you create, you should put in the folder
- copy the folder 'vs' to the folder

You should get this strutcture:
* folder
  * main.py
  * rescuer.py
  * explorer.py
  * vs
    * abstract_agent.py
    * constants.py
    * environment.py
    * physical_agent.py
         
