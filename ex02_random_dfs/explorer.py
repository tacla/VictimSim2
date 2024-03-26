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
from astar_algorithm import AStarExplorer
from map import Map
from state import State

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
    instance_count = 0  #Class variable to keep track of the count of instances

    def __init__(self, env, config_file, resc):
        """ Construtor do agente random on-line
        @param env: a reference to the environment 
        @param config_file: the absolute path to the explorer's config file
        @param resc: a reference to the rescuer agent to invoke when exploration finishes
        """

        super().__init__(env, config_file)
        Explorer.instance_count += 1
        self.id = Explorer.instance_count  #Unique id for the explorer
        self.walk_stack = Stack()  # a stack to store the movements
        self.set_state(VS.ACTIVE)  # explorer is active since the begin
        self.resc = resc           # reference to the rescuer agent
        self.x = 0                 # current x position relative to the origin 0
        self.y = 0                 # current y position relative to the origin 0
        self.map = Map()           # create a map for representing the environment
        self.victims = {}          # a dictionary of found victims: (seq): ((x,y), [<vs>])
                                   # the key is the seq number of the victim,(x,y) the position, <vs> the list of vital signals
        self.action_order = {
            'N' : 0,
            'S' : 1,
            'E' : 2,
            'W' : 3,
            'NO' : 4,
            'NE' : 5,
            'SO' : 6,
            'SE' : 7
        }
        self.visited = []           #array of visited states
        self.move_concluded = False #boolean to check if the movement was completed

        # put the current position - the base - in the map
        self.map.add((self.x, self.y), 1, VS.NO_VICTIM, self.check_walls_and_lim())

    def get_next_position(self):
        """ Randomically, gets the next position that can be explored (no wall and inside the grid)
            There must be at least one CLEAR position in the neighborhood, otherwise it loops forever.
        """
        # Check the neighborhood walls and grid limits
        obstacles = self.check_walls_and_lim()
    
        # Loop until a CLEAR position is found
        while True:
            # Get a random direction
            direction = random.randint(0, 7)
            # Check if the corresponding position in walls_and_lim is CLEAR
            if obstacles[direction] == VS.CLEAR:
                return Explorer.AC_INCR[direction]
        
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
            print("******")
            print("achou uma parede em:")  
            print(self.x, self.y)  
            self.map.add((self.x + dx, self.y + dy), VS.OBST_WALL, VS.NO_VICTIM, self.check_walls_and_lim())
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
            self.map.add((self.x, self.y), difficulty, seq, self.check_walls_and_lim())
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
            print(f"{self.NAME}: coming back at ({self.x}, {self.y}), rtime: {self.get_rtime()}")
        
    def DFS_online(self):
        if (self.x == 0 and self.y == 0):  #if the agent is in the base   
            if self.id == 1:   #first agent's sequence of actions
                actions = ["N","S","E","W","NO","NE","SO","SE"]
            elif self.id == 2: #second agent's sequence of actions
                actions = ["N","E","W","S","SO","NE","NO","SE"]
            elif self.id == 3: #third agent's sequence of actions
                actions = ["NE","E","S","SO","W","N","NO","SE"]
            else:              #fourth agent's sequence of actions
                actions = ["E","W","S","N","SE","S0","NO","SE"]

            initial_state = State(actions,self.action_order)
            self.visited.append(initial_state)  #add first state to the visited array
            self.move_concluded = True
            return self.action_order[actions[0]]  #return first action
        else:
            return
            # if (self.move_concluded):

    def deliberate(self) -> bool:
        """ The agent chooses the next action. The simulator calls this
        method at each cycle. Must be implemented in every agent"""

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
            self.resc.go_save_victims(self.map, self.victims)
            return False

        return self.come_back_with_astar()
        

# **************
#  A-star
# *************

    # Chama o algoritmo do a* para achar o menor caminho
    def find_shortest_path(self, graph, start, goal):
        astar = AStarExplorer(graph, start, goal, self.COST_DIAG, self.COST_LINE, self.map)
        path = list(astar.find_path())
        return path

    # Retorna um objeto adjacency_matrix[i][j], que vale 1 se há uma aresta entre os vértices i e j, e 0 caso contrário. 
    # Cada vértice na matriz corresponde a uma posição visitada pelo agente no mapa.
    def build_adjacency_matrix(self):
        adjacency_matrix = [[0] * len(self.map.map_data) for _ in range(len(self.map.map_data))]

        # Mapeia as coordenadas visitadas para seus índices na matriz
        coord_to_index = {}
        index = 0
        for coord in self.map.map_data.keys():
            coord_to_index[coord] = index
            index += 1

        # Preenche a matriz de adjacências
        for coord, data in self.map.map_data.items():
            x, y = coord
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue  # Ignora a própria posição
                    neighbor_coord = (x + dx, y + dy)
                    if self.map.in_map(neighbor_coord):
                        # Se a vizinhança foi visitada, atualize a matriz de adjacências
                        if data[0] != VS.WALL and self.map.map_data[neighbor_coord][0] != VS.WALL:
                            adjacency_matrix[coord_to_index[coord]][coord_to_index[neighbor_coord]] = 1

        return adjacency_matrix

    def come_back_with_astar(self):
        # monta grafo com as posicoes exploradas (o mapa) usando matriz de adjacencias
        adjacency_matrix = self.build_adjacency_matrix()

        # Uso do A* para achar o caminho mais curto de volta
        shortest_path = self.find_shortest_path(adjacency_matrix, (self.x, self.y), (0, 0))
        print("************************** caminho mais curto para explorador voltar:")
        print(shortest_path)
        
        # Verificar se o caminho foi encontrado
        if len(shortest_path) >= 2:
            # O próximo movimento será a próxima posição no caminho mais curto
            print("agente explorador esta na posicao: ")
            print(shortest_path[0])
            print("proxima posicao: ")
            next_position = shortest_path[1]  # A primeira posição é a atual
            print(next_position)
            dx = next_position[0] - self.x
            dy = next_position[1] - self.y

            # Executar o movimento
            result = self.walk(dx, dy)

            # Verificar se o movimento foi bem-sucedido
            if result == VS.EXECUTED:
                # Atualizar a posição do agente
                self.x = next_position[0]
                self.y = next_position[1]
                return True
            elif result == VS.BUMPED:
                print(f"{self.NAME}: when coming back bumped at ({self.x+dx}, {self.y+dy}) , rtime: {self.get_rtime()}")
                return False
        else:
            # Se o caminho não foi encontrado, não há ação a ser tomada
            print("Caminho não encontrado.")
            return False