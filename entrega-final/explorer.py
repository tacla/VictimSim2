# EXPLORER AGENT
# @Author: Tacla, UTFPR
#
### It walks randomly in the environment looking for victims. When half of the
### exploration has gone, the explorer goes back to the base.

import sys
import os
import random
import math
from abc import ABC, abstractmethod
from vs.abstract_agent import AbstAgent
from vs.constants import VS
from map import Map

class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.is_empty():
            return self.items.pop()

    def is_empty(self):
        return len(self.items) == 0

class Explorer(AbstAgent):
    """ class attribute """
    MAX_DIFFICULTY = 30             # the maximum degree of difficulty to enter into a cell

    x,y = 0,0
    dfs_untried = {}
    dfs_result = {}
    unbacktracked = {}
    visited_cells = [(x,y)]    # record for visited cells
    last_position, last_movement = None, None
    flag_explore = True
    is_unbacktracking = False
    
    def __init__(self, env, config_file, resc):
        """ Construtor do agente random on-line
        @param env: a reference to the environment 
        @param config_file: the absolute path to the explorer's config file
        @param resc: a reference to the rescuer agent to invoke when exploration finishes
        """

        super().__init__(env, config_file)
        self.walk_stack = Stack()  # a stack to store the movements
        self.walk_time = 0         # time consumed to walk when exploring (to decide when to come back)
        self.set_state(VS.ACTIVE)  # explorer is active since the begin
        self.resc = resc           # reference to the rescuer agent
        self.x = 0                 # current x position relative to the origin 0
        self.y = 0                 # current y position relative to the origin 0
        self.map = Map()           # create a map for representing the environment
        self.victims = {}          # a dictionary of found victims: (seq): ((x,y), [<vs>])
                                   # the key is the seq number of the victim,(x,y) the position, <vs> the list of vital signals

        # put the current position - the base - in the map
        self.map.add((self.x, self.y), 1, VS.NO_VICTIM, self.check_walls_and_lim())


    def search_key(self, dict, state, target):
            for key, value in dict.items():
                if state in key:
                    if value == target:
                        return key


    # 0: (0, -1),  #  u: Up
    # 1: (1, -1),  # ur: Upper right diagonal
    # 2: (1, 0),   #  r: Right
    # 3: (1, 1),   # dr: Down right diagonal
    # 4: (0, 1),   #  d: Down
    # 5: (-1, 1),  # dl: Down left left diagonal
    # 6: (-1, 0),  #  l: Left
    # 7: (-1, -1)  # ul: Up left diagonal        
    def actions(self, state):
        order_toGoal = {
            "EXPL_1": [1, 2, 0, 3, 7, 4, 6, 5], # Corner Up Right 
            "EXPL_2": [7, 6, 0, 1, 5, 4, 2, 3], # Corner Up Left 
            "EXPL_3": [5, 6, 4, 7, 3, 0, 2, 1], # Corner Down Left 
            "EXPL_4": [3, 2, 4, 5, 1, 0, 6, 7], # Corner Down Right 
        }
        
        # Obtem a ordem baseada no nome do robô
        if self.walk_time <= 1000:
            order = order_toGoal.get(self.NAME, list(self.AC_INCR.keys()))
        else:
            order = list(self.AC_INCR.keys())
            random.shuffle(order)
        
        if state in self.dfs_untried:
            # Ordena as ações restantes de acordo com a ordem definida para o robô
            return sorted(self.dfs_untried[state], key=lambda x: order.index(x))
        else:
            # Retorna todas as ações, já ordenadas pela sequência do robô
            return order
        

    def add_unbacktracked(self, state):
        if self.last_position != state:
            if state not in list(self.unbacktracked.keys()):
                self.unbacktracked[state] = [self.last_position]
            else:
                self.unbacktracked[state].insert(0,self.last_position)


    def manhattan_distance(self, position):
        return abs(position[0])+abs(position[1])


    # Function to explore map while have time remaining
    def online_dfs(self, position):
        if position not in self.dfs_untried:
            self.dfs_untried[position] = self.actions(position)
        
        # Checa se moveu-se para um novo estado, se sim e não esta em backtracking, adiciona o last_state para backtracking
        if self.last_position != None and self.last_position != position:
            self.dfs_result[(self.last_position, self.last_movement)] = position
            if not self.is_unbacktracking:
                self.add_unbacktracked(position)

        # Checa se já realizou todas as ações possiveis para o estado atual
        if len(self.dfs_untried[position]) == 0:
            if len(self.unbacktracked[position]) == 0:
                return (0,0)
            else:
                unback_pos = self.unbacktracked[position][0]
                del(self.unbacktracked[position][0])

                self.is_unbacktracking = True
                
                memory = self.dfs_result
                self.last_movement = self.search_key(memory, position, unback_pos)[1]
        else:
            self.is_unbacktracking = False
            self.last_movement = self.dfs_untried[position][0]
            del(self.dfs_untried[position][0])

        self.last_position = position
        #print(f'State:{state}\nUntried{self.dfs_untried[state]}')
        #if len(self.unbacktracked) != 0:
        #    print(f'Unback:{self.unbacktracked[state]}\n')
        return self.last_movement

    def reconstruct_path(self, came_from, current):
        total_path = [current]
        while current in came_from.keys():
            current = came_from[current]
            total_path.append(current)
        return total_path   


    def return_neighbors(self, state):
        neighbors = []
        
        for i in range(-1,2):
            for j in range(-1,2):
                neighbor = state[0]+i, state[1]+j
                if neighbor in self.visited_cells and neighbor != state:
                    neighbors.append(neighbor)
        return neighbors


    def cost(self, current, neighbor):
        dx = neighbor[0] - current[0]
        dy = neighbor[1] - current[1]
        if dx != 0 and dy != 0:
            return self.COST_DIAG
        return self.COST_LINE
    

    def a_star(self, start, goal, h):
        open_set = {start}
        came_from = {}
        g_score = {}
        f_score = {}

        for e in self.visited_cells:
            g_score[e] = math.inf
            f_score[e] = math.inf
        
        g_score[start] = 0
        f_score[start] = h(start)

        while len(open_set) != 0:
            value = math.inf
            for e in open_set:
                if f_score[e] < value:
                    current = e
                    value = f_score[e]

            if current == goal:
                return self.reconstruct_path(came_from, current)
            #print(f'open set: {open_set}')
            open_set.remove(current)

            for neighbor in self.return_neighbors(current):
                
                tentative_gscore = g_score[current] + self.cost(current, neighbor)
                if tentative_gscore < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_gscore
                    f_score[neighbor] = tentative_gscore + h(neighbor)
                    if neighbor not in open_set:
                        open_set.add(neighbor)
        print('Erro!')
        return EOFError 
    

    def get_next_position(self):
        """ Randomically, gets the next position that can be explored (no wall and inside the grid)
            There must be at least one CLEAR position in the neighborhood, otherwise it loops forever.
        """
        # Check the neighborhood walls and grid limits
        obstacles = self.check_walls_and_lim()
    
        # Loop until a CLEAR position is found
        while True:

            movement = self.online_dfs((self.x, self.y))
            # Check if the corresponding position in walls_and_lim is CLEAR
            if obstacles[movement] == VS.CLEAR:
                return Explorer.AC_INCR[movement]
        
    def explore(self):
        # get an random increment for x and y       
        dx, dy = self.get_next_position()

        # Moves the body to another position  
        rtime_bef = self.get_rtime()
        result = self.walk(dx, dy)
        rtime_aft = self.get_rtime()


        # Test the result of the walk action
        # Should never bump, but for safe functionning let's test
        if result == VS.BUMPED:
            # update the map with the wall
            self.map.add((self.x + dx, self.y + dy), VS.OBST_WALL, VS.NO_VICTIM, self.check_walls_and_lim())
            #print(f"{self.NAME}: Wall or grid limit reached at ({self.x + dx}, {self.y + dy})")

        if result == VS.EXECUTED:
            # check for victim returns -1 if there is no victim or the sequential
            # the sequential number of a found victim
            self.walk_stack.push((dx, dy))

            # update the agent's position relative to the origin
            self.x += dx
            self.y += dy
            self.visited_cells.append((self.x, self.y))
            
            # update the walk time
            self.walk_time = self.walk_time + (rtime_bef - rtime_aft)
            #print(f"{self.NAME} walk time: {self.walk_time}")

            # Check for victims
            seq = self.check_for_victim()
            if seq != VS.NO_VICTIM:
                vs = self.read_vital_signals()
                self.victims[vs[0]] = ((self.x, self.y), vs)
                #print(f"{self.NAME} Victim found at ({self.x}, {self.y}), rtime: {self.get_rtime()}")
                #print(f"{self.NAME} Seq: {seq} Vital signals: {vs}")
            
            # Calculates the difficulty of the visited cell
            difficulty = (rtime_bef - rtime_aft)
            if dx == 0 or dy == 0:
                difficulty = difficulty / self.COST_LINE
            else:
                difficulty = difficulty / self.COST_DIAG

            # Update the map with the new cell
            self.map.add((self.x, self.y), difficulty, seq, self.check_walls_and_lim())
            #print(f"{self.NAME}:at ({self.x}, {self.y}), diffic: {difficulty:.2f} vict: {seq} rtime: {self.get_rtime()}")

        return

    def come_back(self):
        self.flag_explore = False
        to_walk = self.a_star((self.x, self.y), (0,0), self.manhattan_distance)

        # Moves the body to another position
        if len(to_walk) > 1:
            dx, dy = to_walk[-2][0] - to_walk[-1][0], to_walk[-2][1] - to_walk[-1][1]
            to_walk.pop()
        else:
            dx, dy = to_walk.pop()
        # dx, dy = self.walk_stack.pop()
        # dx = dx * -1
        # dy = dy * -1
        result = self.walk(dx, dy)
        if result == VS.BUMPED:
            print(f"{self.NAME}: when coming back bumped at ({self.x+dx}, {self.y+dy}) , rtime: {self.get_rtime()}")
            return
        
        if result == VS.EXECUTED:
            # update the agent's position relative to the origin
            self.x += dx
            self.y += dy
            #print(f"{self.NAME}: coming back at ({self.x}, {self.y}), rtime: {self.get_rtime()}")
        
    def deliberate(self) -> bool:
        """ The agent chooses the next action. The simulator calls this
        method at each cycle. Must be implemented in every agent"""

        # keeps exploring while there is enough time
        if self.get_rtime() > self.manhattan_distance((self.x, self.y))*self.COST_LINE*1.5 + self.MAX_DIFFICULTY and self.flag_explore:
            self.explore()
            return True

        # no more come back walk actions to execute or already at base
        #if self.walk_stack.is_empty() or 
        if (self.x == 0 and self.y == 0):
            # time to pass the map and found victims to the master rescuer
            self.resc.sync_explorers(self.map, self.victims)
            # finishes the execution of this agent
            return False
        
        # proceed to the base
        self.come_back()
        return True

