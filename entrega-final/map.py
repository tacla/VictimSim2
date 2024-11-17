# Map Class
# @Author: Cesar A. Tacla, UTFPR
#
## A map representing the explored region of the 2D grid
## The map is a dictionaire whose keys are pairs (x, y).
## The map contains only visited positions.
##
## An entry in the dictionary is: [(x,y)] : ( difficulty, vic_id, [actions' results] )
## - (x,y): the key; the position of the grid (or the cell)
## - difficulty: the degree of difficulty to access the cell
## - vic_id: the victim identification number (if there is one) or VS.NO_VICTIM if there is no victim
## - actions' results: the known actions' results from the cell represented as vector of 8 integers, in the following
##   order: [up, up-right, right, down-right, down, down-left, left, up-left]. Each position may
##   have the following values:
##   VS.UNK  the agent ignores if it is possible to go towards the direction (useful if you want
##           to not use the check_walls_and_lim method of the AbstAgent and save only tried actions)
##   VS.WALL the agent cannot execute the action (there is a wall),
##   VS.END  the agent cannot execute the action (end of grid)
##   VS.CLEAR the agent can execute the action
##
## Example of a map entry WITH VICTIM:
## (10, 8): (3.0, 10, [VS.WALL, VS.WALL, VS.CLEAR, VS.CLEAR, VS.WALL, VS.END, VS.END, VS.END])
## the position x=10, y=8 has a difficulty of 3.0 and the victim number 10 is there.
##   +--+--+--+--+
##   !!!|XX|XX|    
##   +--+--+--+--+      AG is the currently visited position (10,8) where the victim 10 is located
##   !!!|AG|  |         XX is a wall (
##   +--+--+--+--+      !! is the end of the grid
##   !!!|XX|  |       
##   +--+--+--+--+
##
## Example of a map entry WITHOUT VICTIM:
## (11, 8): (0, VS.NO_VICTIM,[VS.WALL, VS.CLEAR, VS.CLEAR, VS.CLEAR, VS.CLEAR, VS.WALL, VS.CLEAR, VS.WALL])   
##
from vs.constants import VS

class Map:
    def __init__(self):
        self.data = {}

    
    def in_map(self, coord):
        if coord in self.data:
            return True

        return False        
                
    def get(self, coord):
        """ get all the values associated to a coord key: a triple (diff, vic_id, [actions' results])
            @param coord: a pair (x, y), the key of the dictionary"""
        return self.data.get(coord)

    def get_difficulty(self, coord):
        """ get only the difficulty value associated to a coord key: a triple (diff, vic_id, [actions' results])
            @param coord: a pair (x, y), the key of the dictionary"""
        return self.data.get(coord)[0]

    def get_vic_id(self, coord):
        """ get only the victim id number associated to a coord key: a triple (diff, vic_id, [actions' results])
            @param coord: a pair (x, y), the key of the dictionary"""
        return self.data.get(coord)[1]

    def get_actions_results(self, coord):
        """ get only the actions' results associated to a coord key: a triple (diff, vic_id, [actions' results])
            @param coord: a pair (x, y), the key of the dictionary"""
        return self.data.get(coord)[2]

        
    def add(self, coord, difficulty, vic_id, actions_res):
        """ @param coord: a pair (x, y)
            @param difficulty: the degree of difficulty to acess the cell at coord
            @param vic_id: the id number of the victim returned by the Environment
            @param actions_res: the results of the possible actions from the position (x, y) """
        self.data[coord] = (difficulty, vic_id, actions_res)

    def update(self, another_map):
        """ Itupdates the current map with the entries of another map.
            If the keys are identical, the entry of the another map replaces the entry of the current map.
            @param another_map: other instance of Map """
        self.data.update(another_map.data)

    def draw(self):
        if not self.data:
            print("Map is empty.")
            return

        min_x = min(key[0] for key in self.data.keys())
        max_x = max(key[0] for key in self.data.keys())
        min_y = min(key[1] for key in self.data.keys())
        max_y = max(key[1] for key in self.data.keys())

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


    
