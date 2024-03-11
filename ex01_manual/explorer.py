## EXPLORER AGENT
### @Author: Tacla, UTFPR
### It walks randomly in the environment looking for victims.

import sys
import os
import random
from abc import ABC, abstractmethod
from vs.abstract_agent import AbstAgent
from vs.constants import VS



class Explorer(AbstAgent):
    def __init__(self, env, config_file, resc):
        """ Construtor do agente random on-line
        @param env referencia o ambiente
        @config_file: the absolute path to the explorer's config file
        @param resc referencia o rescuer para poder acorda-lo
        """
        super().__init__(env, config_file)
        self.set_state(VS.ACTIVE)
        
        # Specific initialization for the rescuer
        self.resc = resc           # reference to the rescuer agent   
    
    def deliberate(self) -> bool:
        """ The agent chooses the next action. The simulator calls this
        method at each cycle. Must be implemented in every agent"""

        print(f"\n{self.NAME} deliberate:")
        # No more actions, time almost ended
        if self.get_rtime() <= 1.0:
            # time to wake up the rescuer
            # pass the walls and the victims (here, they're empty)
            print(f"{self.NAME} No more time to explore... invoking the rescuer")
            self.resc.go_save_victims([],[])
            return False
        
        dx = 0
        dy = 0
        print(f"Enter u(UP) d(DOWN) l(LEFT) r(RIGHT) ul(UP LEFT) ur(UP RIGHT) dl(DOWN LEFT) dr(DOWN RIGHT) x(EXIT)")
        tecla = input(">>> ").lower()

        if tecla == "u":
           dy=-1
        elif tecla == "d":
           dy=1
        elif tecla == "l":
           dx=-1
        elif tecla == "r":
           dx = 1
        elif tecla == "ul":
            dx = -1
            dy = -1
        elif tecla == "dl":
            dx = -1
            dy = 1
        elif tecla == "ur":
            dx = 1
            dy = -1
        elif tecla == "dr":
            dx = 1
            dy = 1
        elif tecla == "x":
            print(f"{self.NAME} exploring phase terminated... invoking the rescuer")
            self.resc.go_save_victims([],[])
            return False
        
        # Moves the body to another position
        result = self.walk(dx, dy)

        # Test the result of the walk action
        if result == VS.BUMPED:
            walls = 1  # build the map- to do
            print(f"{self.NAME}: wall or grid limit reached")

        if result == VS.EXECUTED:
            # check for victim returns -1 if there is no victim or the sequential
            # the sequential number of a found victim
            print(f"{self.NAME} walk executed, rtime: {self.get_rtime()}")
            seq = self.check_for_victim()
            if seq >= 0:
                vs = self.read_vital_signals()
                print(f"{self.NAME} Vital signals read, rtime: {self.get_rtime()}")
                print(f"{self.NAME} Vict: {vs[0]}\n     pSist: {vs[1]:.1f} pDiast: {vs[2]:.1f} qPA: {vs[3]:.1f}")
                print(f"     pulse: {vs[4]:.1f} frResp: {vs[5]:.1f}")  
               
        return True

