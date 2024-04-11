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
from time import sleep, time

from vs.abstract_agent import AbstAgent
from vs.constants import VS
from map import Map, Position

devagarinho = 0
class Explorer(AbstAgent):
    def __init__(self, env, config_file, boss, priority):
        """ Construtor do agente random on-line
        @param env: a reference to the environment 
        @param config_file: the absolute path to the explorer's config file
        @param resc: a reference to the rescuer agent to invoke when exploration finishes
        """

        super().__init__(env, config_file)
        self.set_state(VS.ACTIVE)  # explorer is active since the begin
        self.boss = boss           # reference to the rescuer agent
        self.x = 0                 # current x position relative to the origin 0
        self.y = 0                 # current y position relative to the origin 0
        self.map = Map()           # create a map for representing the environment
        self.victims = {}          # a dictionary of found victims: (seq): ((x,y), [<vs>])
                                   # the key is the seq number of the victim,(x,y) the position, <vs> the list of vital signals
        self.walked = 0
        self.returning = []
        self.returning_base = False
        self.in_strategy = True
        self.priority = priority

        # put the current position - the base - in the map
        self.map.add(Position(coords=(self.x, self.y), difficulty=1, visited=True))

    def get_next_position(self, actual_pos):
        global devagarinho, backt
        obstacles = self.check_walls_and_lim()
        actual_pos.agent_seq = obstacles

        next_pos = None

        for i in self.priority:
            if obstacles[i] != VS.CLEAR:
                continue

            coords = (self.x + Explorer.AC_INCR[i][0], self.y + Explorer.AC_INCR[i][1])
            pos = self.map.get_or_create(coords)
            actual_pos.neighborhood[coords] = pos
            pos.neighborhood[actual_pos.coords] = actual_pos

            if next_pos is None and not pos.visited:
                next_pos = Explorer.AC_INCR[i]

        if next_pos is None:
            back_pos = self.map.get_closest_not_visited(actual_pos)
            if back_pos is None:
                self.returning_base = True
                back_pos = self.map.get((0, 0))

            self.returning = self.map.get_path(actual_pos, back_pos, self)[1:]
            return self.get_returning_direction()


        return next_pos


    def explore(self):
        old_pos = self.map.get_or_create((self.x, self.y))
        old_pos.visited = True

        dx, dy = self.get_next_position(old_pos)

        rtime_bef = self.get_rtime()
        result = self.walk(dx, dy)
        rtime_aft = self.get_rtime()

        if result != VS.EXECUTED:
            print(f"{self.NAME} deu problema: {result} no {self.x, self.y} indo para {dx, dy}")
            return

        self.x += dx
        self.y += dy

        seq = self.check_for_victim()
        if seq != VS.NO_VICTIM and self.map.get_or_create((self.x, self.y)).victim_seq == VS.NO_VICTIM:
            self.map.get_or_create((self.x, self.y)).victim_seq = seq
            vs = self.read_vital_signals()
            self.victims[vs[0]] = ((self.x, self.y), vs)
            print(f"{self.NAME} Victim found at ({self.x}, {self.y}), rtime: {self.get_rtime()}")

        difficulty = (rtime_bef - rtime_aft)
        if dx == 0 or dy == 0:
            old_pos.difficulty = difficulty / self.COST_LINE
        else:
            old_pos.difficulty = difficulty / self.COST_DIAG

        self.walked += difficulty
        return

    def return_to_base(self):
        dx, dy = self.get_returning_direction()

        result = self.walk(dx, dy)

        if result != VS.EXECUTED:
            print(f"{self.NAME} deu problema voltando pra base: {result} no {self.x, self.y} indo para {dx, dy}")
            return

        self.x += dx
        self.y += dy
        return

    def get_returning_direction(self):
        actual_pos = self.map.get_or_create((self.x, self.y))
        next_pos = self.returning.pop(0)
        return ((actual_pos.coords[0] - next_pos.coords[0]) * -1, (actual_pos.coords[1] - next_pos.coords[1]) * -1)

    def deliberate(self) -> bool:
        """ The agent chooses the next action. The simulator calls this
        method at each cycle. Must be implemented in every agent"""
        sleep(devagarinho)

        pos = self.map.get_or_create((self.x, self.y))

        if self.returning_base and self.x == 0 and self.y == 0:
            print(f"{self.NAME}: rtime {self.get_rtime()}, invoking the rescuer")
            self.boss.alert_explorer_inactive(self.map, self.victims)
            return False

        if self.returning_base:
            self.return_to_base()
            return True

        if self.get_rtime() < self.walked + (3 * max(self.COST_LINE, self.COST_DIAG)) + self.COST_READ:
            self.walked = self.map.time_to_return(pos, self)
            if self.get_rtime() < self.walked + 50:
                actual_pos = self.map.get_or_create((self.x, self.y))
                self.returning = self.map.get_path(actual_pos, self.map.get((0, 0)), self)
                self.returning_base = True
                self.return_to_base()
                return True
            
        if len(self.returning) != 0:
            self.return_to_base()
            return True

        self.explore()
        return True
