This folder contains python programs to upgrade configuration files from VictimSim1 to 2.

transf_walls_to_vs2.py
----------------------
Transforms the old version of env_walls.txt to the new env_obsts.txt. In version 2, we added the degree of difficulty to access each cell. Besides, walls are now represented by the integer 100 (VS.OBST_WALL).
