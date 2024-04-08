# EXPLORER AGENT
# @Author: , UTFPR
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

    # shared with all explorers
    num_of_explorers = 0
    map = Map()
    global_victims = []

    def __init__(self, env, config_file, resc):
        """ 
        Construtor do agente random on-line
        @param env: a reference to the environment 
        @param config_file: the absolute path to the explorer's config file
        @param resc: a reference to the rescuer agent to invoke when exploration finishes
        """

        super().__init__(env, config_file)
        self.walk_stack = Stack()  # a stack to store the movements
        self.untried = {}
        self.unbacktracked = {}
        Explorer.num_of_explorers += 1
        self.set_state(VS.ACTIVE)  # explorer is active since the begin
        self.resc = resc           # reference to the rescuer agent
        self.x = 0                 # current x position relative to the origin 0
        self.y = 0                 # current y position relative to the origin 0
        self.victims = {}          # a dictionary of found victims: (seq): ((x,y), [<vs>])
                                   # the key is the seq number of the victim,(x,y) the position, <vs> the list of vital signals

        # put the current position - the base - in the map
        Explorer.map.add((self.x, self.y), 1, VS.NO_VICTIM, self.check_walls_and_lim())

    def get_next_position(self):
        direction = self.online_DFS()
        return direction

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
            Explorer.map.add((self.x + dx, self.y + dy), VS.OBST_WALL, VS.NO_VICTIM, self.check_walls_and_lim())
            #print(f"{self.NAME}: Wall or grid limit reached at ({self.x + dx}, {self.y + dy})")

        if result == VS.EXECUTED:
            # check for victim returns -1 if there is no victim or the sequential
            # the sequential number of a found victim
            self.walk_stack.push((dx, dy))

            # update the agent's position relative to the origin
            self.x += dx
            self.y += dy          

            # Check for victims
            seq = self.check_for_victim()
            if seq != VS.NO_VICTIM:
                vs = self.read_vital_signals()
                self.victims[vs[0]] = ((self.x, self.y), vs)
                print(f"{self.NAME} Victim found at ({self.x}, {self.y}), rtime: {self.get_rtime()}")
                #print(f"{self.NAME} Seq: {seq} Vital signals: {vs}")
            
            # Calculates the difficulty of the visited cell
            difficulty = (rtime_bef - rtime_aft)
            if dx == 0 or dy == 0:
                difficulty = difficulty / self.COST_LINE
            else:
                difficulty = difficulty / self.COST_DIAG

            # Update the map with the new cell
            Explorer.map.add((self.x, self.y), difficulty, seq, self.check_walls_and_lim())
            #print(f"{self.NAME}:at ({self.x}, {self.y}), diffic: {difficulty:.2f} vict: {seq} rtime: {self.get_rtime()}")

        return

    def come_back(self):
        dx, dy = self.walk_stack.pop()
        dx = dx * -1
        dy = dy * -1

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
        """ 
        The agent chooses the next action. The simulator calls this
        method at each cycle. Must be implemented in every agent
        """

        consumed_time = self.TLIM - self.get_rtime()
        if consumed_time < self.get_rtime():
            self.explore()
            return True

        # time to come back to the base
        if self.walk_stack.is_empty() or (self.x == 0 and self.y == 0):
            # time to wake up the rescuer
            # pass the walls and the victims (here, they're empty)
            print(f"{self.NAME}: rtime {self.get_rtime()}, invoking the rescuer")
            #input(f"{self.NAME}: type [ENTER] to proceed")

            Explorer.global_victims.append(self.victims)
            Explorer.num_of_explorers -= 1

            if (Explorer.num_of_explorers == 0):
                # the last explorer calls the rescuer
                self.resc.go_save_victims(Explorer.map, Explorer.global_victims.copy())
                 
            return False

        self.come_back()
        return True

    def online_DFS(self):
        """
        Perform online DFS.
        """

        # Check the neighborhood walls and grid limits
        obstacles = self.check_walls_and_lim()

        # Current state
        state = (self.x, self.y)

        # 8 possible directions
        directions = list(range(8))

        # Add the current state if it was not explored
        if state not in self.untried:
            self.untried[state] = directions
            random.shuffle(self.untried[state]) # if not random, explorers go all the same way
        
        # Explores every untried direction
        while self.untried[state]:

            # next state
            next_direction = self.untried[state][0]
            dx, dy = self.AC_INCR[next_direction] # increment

            obstacle = obstacles[next_direction] # {CLEAR, WALL, END}

            if obstacle == VS.WALL or obstacle == VS.END: # wall or end state
                # can not continue, pop
                self.untried[state].pop(0)
            elif obstacle == VS.CLEAR: # clear state

                if state not in self.unbacktracked:
                    self.unbacktracked[state] = []
                
                self.unbacktracked[state].append((self.x + dx, self.y + dy))

                # return direction
                return self.AC_INCR[self.untried[state].pop(0)]

        # if can not continue, go back
        if not self.untried[state]:
            return self.unbacktracked[state].pop(0)
