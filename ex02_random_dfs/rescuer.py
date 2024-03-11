##  RESCUER AGENT
### @Author: Tacla (UTFPR)
### Demo of use of VictimSim

import os
import random
from map import Map
from vs.abstract_agent import AbstAgent
from vs.physical_agent import PhysAgent
from vs.constants import VS
from abc import ABC, abstractmethod


## Classe que define o Agente Rescuer com um plano fixo
class Rescuer(AbstAgent):
    def __init__(self, env, config_file):
        """ 
        @param env: a reference to an instance of the environment class
        @param config_file: the absolute path to the agent's config file"""

        super().__init__(env, config_file)

        # Specific initialization for the rescuer
        self.map = None             # explorer will pass the map
        self.victims = None         # list of found victims
        self.plan = []              # a list of planned actions
        self.x_plan = 0             # the x position of the rescuer during the planning phase
        self.y_plan = 0             # the y position of the rescuer during the planning phase
        self.visited_plan = set()   # positions already planned to be visited 
        self.rtime_plan = self.TLIM # the remaing time during the planning phase
        self.walk_time_plan = 0.0   # previewed time to walk during rescue
                
        # Starts in IDLE state.
        # It changes to ACTIVE when the map arrives
        self.set_state(VS.IDLE)

    
    def go_save_victims(self, map, victims):
        """ The explorer sends the map containing the walls and
        victims' location. The rescuer becomes ACTIVE. From now,
        the deliberate method is called by the environment"""

        print(f"\n\n*** R E S C U E R ***")
        self.map = map
        print(f"{self.NAME} Map received from the explorer")
        self.map.draw()

        print()
        print(f"{self.NAME} List of found victims received from the explorer")
        self.victims = victims

        # print the found victims - you may comment out
        for seq, data in self.victims.items():
            coord, vital_signals = data
            x, y = coord
            print(f"{self.NAME} Victim seq number: {seq} at ({x}, {y}) vs: {vital_signals}")

        print(f"{self.NAME} time limit to rescue {self.rtime_plan}")

        self.__planner()
        self.set_state(VS.ACTIVE)
        
    def __depth_search(self, actions_res):
        enough_time = True
        print(f"\n{self.NAME} actions results: {actions_res}")
        for i, ar in enumerate(actions_res):

            if ar == VS.CLEAR:
               dx, dy = Rescuer.AC_INCR[i]  # get the increments for the possible action

               # checks if the explorer visited this position - walks only to known positions -
               # and if it is not  planned to be visited
               if ((self.x_plan + dx, self.y_plan + dy) not in self.visited_plan and
                   self.map.in_map((self.x_plan + dx, self.y_plan + dy))):
                   self.x_plan += dx
                   self.y_plan += dy
                   difficulty, vic_seq, next_actions_res = self.map.get((self.x_plan, self.y_plan))
                   print(f"{self.NAME}: planning to go to ({self.x_plan}, {self.y_plan})")
                                 
                   if dx == 0 or dy == 0:
                       step_cost = self.COST_LINE * difficulty
                   else:
                       step_cost = self.COST_DIAG * difficulty
                       
                   print(f"{self.NAME}: difficulty {difficulty}, step cost {step_cost}")
                   print(f"{self.NAME}: acc walk time {self.walk_time_plan}, rtime {self.rtime_plan}")

                   # check if there is enough remaining time to walk back to the base
                   if self.walk_time_plan + step_cost > self.rtime_plan:
                       enough_time = False
                       print(f"{self.NAME}: no enough time to go to ({self.x_plan}, {self.y_plan}")
                   else:
                       # update walk time and remaining time
                       self.walk_time_plan += step_cost
                       self.rtime_plan -= step_cost
                       self.visited_plan.add((self.x_plan, self.y_plan))
       
                       if vic_seq == VS.NO_VICTIM:
                           self.plan.append((dx, dy, False)) # walk only
                           print(f"{self.NAME}: move planned ({self.x_plan}, {self.y_plan}, False")
                       else:
                           # checks if there is enough remainng time to rescue the victim and
                           # come back to the base
                           if self.rtime_plan - self.COST_FIRST_AID < self.walk_time_plan:
                               print(f"{self.NAME}: no enough time to rescue the victim")
                               enough_time = False
                           else:
                               self.plan.append((self.x_plan, self.y_plan, True))
                               print(f"{self.NAME}: move and rescue planned ({self.x_plan}, {self.y_plan}, True")
                               self.rtime_plan -= self.COST_FIRST_AID

                   if enough_time:
                       self.__depth_search(self.map.get((self.x_plan, self.y_plan))[2]) # actions results

                   return               
        
    
    def __planner(self):
        """ A private method that calculates the walk actions in a OFF-LINE MANNER to rescue the
        victims. Further actions may be necessary and should be added in the
        deliberata method"""

        """ This plan starts at origin (0,0) and chooses the first of the possible actions in a clockwise manner starting at 12h.
        Then, if the next position was visited by the explorer, the rescuer goes to there. Otherwise, it picks the following possible action.
        For each planned action, the agent calculates the time will be consumed. When time to come back to the base arrives,
        it reverses the plan."""

        # This is a off-line trajectory plan, each element of the list is a pair dx, dy that do the agent walk in the x-axis and/or y-axis.
        # Besides, it has a flag indicating that a first-aid kit must be delivered when the move is completed.
        # For instance (0,1,True) means the agent walk to (x+0,y+1) and after walking, it leaves the kit.

        difficulty, vic_seq, actions_res = self.map.get((0,0))
        self.__depth_search(actions_res)

        
    def deliberate(self) -> bool:
        """ This is the choice of the next action. The simulator calls this
        method at each reasonning cycle if the agent is ACTIVE.
        Must be implemented in every agent
        @return True: there's one or more actions to do
        @return False: there's no more action to do """

        # No more actions to do
        if self.plan == []:  # empty list, no more actions to do
           input(f"{self.NAME} has finished the plan [ENTER]")
           return False

        # Takes the first action of the plan (walk action) and removes it from the plan
        dx, dy, there_is_vict = self.plan.pop(0)

        # Walk - just one step per deliberation
        result = self.walk(dx, dy)

        # Rescue the victim at the current position
        if result == VS.EXECUTED:
            # check if there is a victim at the current position
            if there_is_vict:
                res = self.first_aid() # True when rescued

        input(f"{self.NAME} remaining time: {self.get_rtime()} Tecle enter")

        return True

