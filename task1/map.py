# Map Class
# @Author: Cesar A. Tacla, UTFPR
#
## A map representing the explored region of the 2D grid
## The map is a dictionaire whose keys are pairs (x, y).
## The map contains only visited positions.
##
## Associated to each key, there are:
## - the degree of difficulty to access the cell
## - the victim seq number (if there is one) or VS.NO_VICTIM if there is no victim
## - the known actions' results from the cell represented as vector of 8 integers, in the following
##   order: [up, up-right, right, down-right, down, down-left, left, up-left]. Each position may
##   have the following values:
##   VS.UNK  the agent ignores if it is possible to go towards the direction (useful if you want
##           to not use the check_walls_and_lim method of the AbstAgent and save only tried actions)
##   VS.WALL the agent cannot execute the action (there is a wall),
##   VS.END  the agent cannot execute the action (end of grid)
##   VS.CLEAR the agent can execute the action

from vs.constants import VS

class Map:
    def __init__(self):
        self.map_data = {}

    def in_map(self, coord):
        if coord in self.map_data:
            return True

        return False

    def get(self, coord):
        """ @param coord: a pair (x, y), the key of the dictionary"""
        return self.map_data.get(coord)

    def add(self, coord, difficulty, victim_seq, actions_res):
        """ @param coord: a pair (x, y)
            @param difficulty: the degree of difficulty to acess the cell at coord
            @param victim_seq: the sequential number of the victim returned by the Environment
            @param actions_res: the results of the possible actions from the position (x, y) """
        self.map_data[coord] = (difficulty, victim_seq, actions_res)

    def draw(self):
        if not self.map_data:
            print("Map is empty.")
            return

        min_x = min(key[0] for key in self.map_data.keys())
        max_x = max(key[0] for key in self.map_data.keys())
        min_y = min(key[1] for key in self.map_data.keys())
        max_y = max(key[1] for key in self.map_data.keys())

        for y in range(min_y, max_y + 1):
            row = ""
            for x in range(min_x, max_x + 1):
                item = self.get((x, y))
                if item:
                    if item[1] == VS.NO_VICTIM:
                        row += f"[{item[0]:7.2f}  no] "
                    else:
                        row += f"[{item[0]:7.2f} {item[1]:3d}] "
                else:
                    row += f"[     ?     ] "
            print(row)


    
