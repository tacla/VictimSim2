##  ABSTRACT AGENT
### @Author: Tacla (UTFPR)
### It has the default methods for all the agents supposed to run in
### the environment

import os
import random
from abc import ABC, abstractmethod
from .constants import VS

class AbstAgent:
    """ This class represents a generic agent and must be implemented by a concrete class. """

    # Class attributes
    
    # Define increments for the walk actions
    AC_INCR = {
        0: (0, -1),  #  u: Up
        1: (1, -1),  # ur: Upper right diagonal
        2: (1, 0),   #  r: Right
        3: (1, 1),   # dr: Down right diagonal
        4: (0, 1),   #  d: Down
        5: (-1, 1),  # dl: Down left left diagonal
        6: (-1, 0),  #  l: Left
        7: (-1, -1)  # ul: Up left diagonal
    }
    
    def __init__(self, env, config_file):
        """ 
        Any class that inherits from this one will have these attributes available.
        @param env referencia o ambiente
        @param config_file: the absolute path to the agent's config file
        """
        self.NAME = ""              # public: the name of the agent
        self.TLIM = 0.0             # public: time limit to execute (cannot be exceeded)
        self.COST_LINE = 0.0        # public: basic cost to walk one step hor or vertically
        self.COST_DIAG = 0.0        # public: basic cost to walk one step diagonally
        self.COST_READ = 0.0        # public: basic cost to read a victim's vital sign
        self.COST_FIRST_AID = 0.0   # public: basic cost to drop the first aid package to a victim
        self.COLOR = (100,100,100)  # public: color of the agent
        self.TRACE_COLOR = (140,140,140) # public: color for the visited cells
               
        self.__env = env            # private - ref. to the environment
        self.__body = None          # private - ref. to the physical part of the agent in the env
        
        # Read agents config file for controlling time
        with open(config_file, "r") as file:

            # Read each line of the file
            for line in file:
                # Split the line into words
                words = line.split()

                # Get the keyword and value
                keyword = words[0]
                if keyword=="NAME":
                    self.NAME = words[1]
                elif keyword=="COLOR":
                    r = int(words[1].strip('(), '))
                    g = int(words[2].strip('(), '))
                    b = int(words[3].strip('(), '))
                    self.COLOR=(r,g,b)  # a tuple
                elif keyword=="TRACE_COLOR":
                    r = int(words[1].strip('(), '))
                    g = int(words[2].strip('(), '))
                    b = int(words[3].strip('(), '))
                    self.TRACE_COLOR=(r,g,b)  # a tuple
                elif keyword=="TLIM":
                    self.TLIM = float(words[1])
                elif keyword=="COST_LINE":
                    self.COST_LINE = float(words[1])
                elif keyword=="COST_DIAG":
                    self.COST_DIAG = float(words[1])
                elif keyword=="COST_FIRST_AID":
                    self.COST_FIRST_AID = float(words[1])
                elif keyword=="COST_READ":    
                    self.COST_READ = float(words[1])
                    
        # Register the agent within the environment 
        self.__body = env.add_agent(self)
        

    @abstractmethod
    def deliberate(self) -> bool:
        """ This is the choice of the next action. The simulator calls this
        method at each reasonning cycle if and only if the agent is ACTIVE.
        Must be implemented in every agent. The agent should execute only on walk acton per deliberation.
        @return True: there's one or more actions to do
        @return False: there's no more action to do """

        pass

    ## The public methods below, you may use when programming your agent
    def get_rtime(self):
        """ Public method for getting the agent remaining battery time (it's like a gauge)
        @return: the remaining battery time (a float value). When < 0, the agent is dead."""
        return self.__body._rtime
   
    def get_state(self):
        return self.__body._state

    def set_state(self, value):
        """ This protected method allows the environment to change the state of the agent"""
        self.__body._state  = value
        
    def walk(self, dx, dy):
        """ Public method for moving the agent's body one cell to any direction (if possible)
        @param dx: an int value corresponding to deplacement in the x axis
        @param dy: an int value corresponding to deplacement in the y axis
        @returns VS.BUMPED = the agent bumped into a wall or reached the end of grid
        @returns VS.TIME_EXCEEDED = the agent has no enough time to execute the action
        @returns VS.EXECUTED = the action is succesfully executed
        In every case, action's executing time is discounted from time limit"""      
        return self.__body._walk(dx, dy)

    def check_walls_and_lim(self):
        """ Public method for checking walls and the grid limits in the neighborhood of the current position of the agent.
        @returns: a vector of eight integers indexed in a clockwise manner. The first position in the vector is the position
        above the current position of the agent, the second is in the upper right diagonal direction, the third is to the right, and so on.
        Each vector position contains one of the following values: {CLEAR, WALL, END}
        - VS.CLEAR means that there is no obstacle 
        - VS.WALL means that there is a wall 
        - VS.END means the end of the grid 
        """      
        return self.__body._check_walls_and_lim()


    def check_for_victim(self):
        """ Public method for testing if there is a victim at the current position of the agent.
        The victim sequential number starts at zero. Zero corresponds to the first victim of the
        data files env_victims.txt and env_vital_signals.txt, 1 to the 2nd, and so on. 
        @returns:
        - the sequential number of the victim (integer), or
        - VS.NO_VICTIM if there is no victim at the current position of the agent. """

        return self.__body._check_for_victim()

    def read_vital_signals(self):
        """ Public method for reading the vital signals of a victim at the same position of the agent.
        Every tentative of reading the vital signal out of position consumes time
        @returns:
        - VS.TIME_EXCEEDED if the agent has no enough battery time to read the vital signals or
        - the list of vital signals (if there is a victim at the current agent's position), composed by
          <seq, pSist, pDiast, qPA, pulse, respiratory freq>, or
        - an empty list if there is no victim at the current agent's position."""
        return self.__body._read_vital_signals()

    def first_aid(self):
        """ Public method for dropping the first aid package to the victim at the same position of the agent.
        @returns:
        - VS.TIME_EXCEEDED when the agent has no enough battery time to execute the operation
        - True when the first aid is succesfully delivered
        - False when there is no victim at the current position of the agent"""
        return self.__body._first_aid()


