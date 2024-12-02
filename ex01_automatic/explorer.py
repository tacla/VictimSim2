import sys
import os
import random
import time
from abc import ABC, abstractmethod
from vs.abstract_agent import AbstAgent
from vs.constants import VS

UP			= ( 0,-1, 'UP')
DOWN		= ( 0, 1, 'DOWN')
LEFT		= (-1, 0, 'LEFT')
RIGHT		= ( 1, 0, 'RIGHT')
UP_LEFT 	= (-1,-1, 'UP_LEFT')
UP_RIGHT	= ( 1,-1, 'UP_RIGHT')
DOWN_LEFT	= (-1, 1, 'DOWN_LEFT')
DOWN_RIGHT	= ( 1, 1, 'DOWN_RIGHT')
STOP 		= ( 0, 0, 'STOP')

class Explorer(AbstAgent):
    def __init__(self, env, config_file, rescuer):
        """ Construtor do agente random on-line
        @param env referencia o ambiente
        @config_file: the absolute path to the explorer's config file
        @param resc referencia o rescuer para poder acorda-lo
        """
        super().__init__(env, config_file)
        self.set_state(VS.ACTIVE)
        self.rescuer = rescuer # Reference to the rescuer agent

        self.steps = [ RIGHT, RIGHT, RIGHT, DOWN_RIGHT, DOWN, DOWN_RIGHT, DOWN_RIGHT, DOWN_RIGHT, DOWN_RIGHT, DOWN, RIGHT, UP_RIGHT, DOWN_LEFT, DOWN, DOWN, DOWN, UP_LEFT, LEFT, UP_LEFT, UP_LEFT, LEFT, LEFT, UP_LEFT, UP_LEFT, UP_LEFT, UP, UP, UP, UP, STOP]

        self.rescuer_steps = []

    def next_move(self):
        next_move = self.steps.pop(0)
        dx = next_move[0]
        dy = next_move[1]
        self.rescuer_steps.append((dx, dy))
        return next_move

    def deliberate(self) -> bool:
        """ The agent chooses the next action. The simulator calls this method at each cycle. Must be implemented in every agent """

        print(f"\n{self.NAME} deliberate:")
        # No more actions, time almost ended
        if self.get_rtime() <= 1.0:
            # time to wake up the rescuer
            # pass the walls and the victims (here, they're empty)
            print(f"{self.NAME} No more time to explore... invoking the rescuer")
            self.rescuer.go_save_victims(self.rescuer_steps,[])
            return False
        
        next_move = self.next_move()

        # print(f"Enter u(UP) d(DOWN) l(LEFT) r(RIGHT) ul(UP LEFT) ur(UP RIGHT) dl(DOWN LEFT) dr(DOWN RIGHT) x(EXIT)")
        # next_move = input(">>> ").lower()

        if next_move == STOP:
            print(f"{self.NAME} exploring phase terminated... invoking the rescuer")
            self.rescuer.go_save_victims(self.rescuer_steps,[])
            return False
        
        print(f'Nextmove: {next_move[2]}')
        
        # Moves the body to another position
        result = self.walk(next_move[0], next_move[1])

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
        
        time.sleep(0.5)

        return True

