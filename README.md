VictimSim2
==========

A simulator designed for testing search algorithms and other IA techniques in rescue scenarios is utilized within the Artificial Intelligence course at UTFPR, Curitiba. Known as VictimSim2, this simulator is useful for studying catastrophic scenarios within a 2D grid environment, where artificial agents embark on search and rescue missions to locate and aid victims.

Key features of the simulator
-----------------------------

- The environment comprises a 2D grid, indexed by coordinates (row, column) or (x, y). The origin is situated at the upper left corner, with the x-axis extending downwards and the y-axis extending towards the right. While the absolute coordinates are accessible solely to the environment simulator, users are encouraged to establish their own coordinate system for the agents.
- Each cell within the 2D grid is assigned a degree of difficulty for accessibility, ranging from values greater than zero to 100. The maximum value of 100 indicates the presence of an impassable wall, while higher values signify increasingly challenging access. Conversely, values less than or equal to one denote easier entry.
- The environment accommodates one or more agents, with each agent assigned a customizable color via configuration files.
- Collision detection is integrated to identify instances where an agent collides with walls or reaches the grid's boundaries, termed as "BUMPED" perception.
- Agents possess the ability to detect obstacles and grid boundaries within their immediate neighborhood, one step ahead from their current position.
- Multiple agents can occupy the same cell simultaneously without causing collisions.
- The simulator regulates the scheduling of each agent based on their state: ACTIVE, IDLE, ENDED, or DEAD. Only active agents are permitted to execute actions, and the simulator manages the allotted execution time for each agent; upon expiry, the agent is considered DEAD.
