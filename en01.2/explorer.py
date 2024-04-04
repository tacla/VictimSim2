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

devagarinho = 0.001
class Explorer(AbstAgent):
    def __init__(self, env, config_file, resc):
        """ Construtor do agente random on-line
        @param env: a reference to the environment 
        @param config_file: the absolute path to the explorer's config file
        @param resc: a reference to the rescuer agent to invoke when exploration finishes
        """

        super().__init__(env, config_file)
        self.set_state(VS.ACTIVE)  # explorer is active since the begin
        self.resc = resc           # reference to the rescuer agent
        self.x = 0                 # current x position relative to the origin 0
        self.y = 0                 # current y position relative to the origin 0
        self.map = Map()           # create a map for representing the environment
        self.victims = {}          # a dictionary of found victims: (seq): ((x,y), [<vs>])
                                   # the key is the seq number of the victim,(x,y) the position, <vs> the list of vital signals
        self.walked = 0
        self.returning = []

        # put the current position - the base - in the map
        self.map.add(Position(coords=(self.x, self.y), difficulty=1, visited=True))

    def get_next_position(self, actual_pos):
        global devagarinho, backt
        obstacles = self.check_walls_and_lim()

        next_pos = None

        for i in range(8): #todo colocar a preferencia da ordem
            if obstacles[i] != VS.CLEAR:
                continue

            coords = (self.x + Explorer.AC_INCR[i][0], self.y + Explorer.AC_INCR[i][1])
            pos = self.map.get_or_create(coords)
            actual_pos.neighborhood[coords] = pos
            pos.neighborhood[actual_pos.coords] = actual_pos

            if next_pos is None and not pos.visited: #todo colocar verificação que não ta fora da strag (ex: se x
                next_pos = Explorer.AC_INCR[i]
                # print(f"{actual_pos.coords} encontrado primeiro loop: {pos}")

        if next_pos is None:
            back_pos = self.map.get_closest_not_visited(actual_pos)
            if back_pos is None:
                print("VOLTANDO")
                back_pos = self.map.get((0, 0))

            self.returning = self.map.get_path(actual_pos, back_pos, self)[1:]
            return (0,0)

        #TODO:
        # 5. verificar se ele ta considerando o caminho segundo a direção (diag, reta)

        return next_pos


    def explore(self):
        pos = self.map.get_or_create((self.x, self.y))

        if (self.x == 57 and self.y == -27) or (self.x == 56 and self.y == -28):
            print(f"marcando {pos} como visited")
        pos.visited = True

        dx, dy = self.get_next_position(pos)

        rtime_bef = self.get_rtime()
        result = self.walk(dx, dy)
        rtime_aft = self.get_rtime()

        if result != VS.EXECUTED:
            raise Exception("não deveria bater")

        self.x += dx
        self.y += dy

        seq = self.check_for_victim()
        if seq != VS.NO_VICTIM:
            vs = self.read_vital_signals()
            self.victims[vs[0]] = ((self.x, self.y), vs)
            print(f"{self.NAME} Victim found at ({self.x}, {self.y}), rtime: {self.get_rtime()}")

        difficulty = (rtime_bef - rtime_aft)
        if dx == 0 or dy == 0:
            pos.difficulty = difficulty / self.COST_LINE
        else:
            pos.difficulty = difficulty / self.COST_DIAG

        self.walked += difficulty
        return

    def return_to_base(self):
        actual_pos = self.map.get_or_create((self.x, self.y))
        next_pos = self.returning.pop(0)
        dx, dy = ((actual_pos.coords[0] - next_pos.coords[0]) * -1, (actual_pos.coords[1] - next_pos.coords[1]) * -1)

        result = self.walk(dx, dy)

        if result != VS.EXECUTED:
            raise Exception("não deveria bater")

        self.x += dx
        self.y += dy
        return

    def deliberate(self) -> bool:
        """ The agent chooses the next action. The simulator calls this
        method at each cycle. Must be implemented in every agent"""
        sleep(devagarinho)

        pos = self.map.get_or_create((self.x, self.y))

        # pos.visited = True
        if self.map.size() != 1 and self.x == 0 and self.y == 0:
            print(f"{self.NAME}: rtime {self.get_rtime()}, invoking the rescuer")
            return False

        if len(self.returning) != 0:
            self.return_to_base()
            return True

        if self.get_rtime() < self.walked + 3:
            self.walked = self.map.time_to_return(pos, self)
            if self.get_rtime() < self.walked + 3:
                actual_pos = self.map.get_or_create((self.x, self.y))
                self.returning = self.map.get_path(actual_pos, self.map.get((0, 0)), self)
                return True

        self.explore()
        return True