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

class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.is_empty():
            return self.items.pop()
    
    def peek(self):
        if not self.is_empty():
            return self.items[-1]  # Acessa o último elemento da lista sem remove-lo

    def is_empty(self):
        return len(self.items) == 0

class Explorer(AbstAgent):
    instance_count = 0  #Class variable to keep track of the count of instances
    """ class attribute """
    MAX_DIFFICULTY = 1             # the maximum degree of difficulty to enter into a cell

    def __init__(self, env, config_file, env_file, resc):
        """ Construtor do agente random on-line
        @param env: a reference to the environment 
        @param config_file: the absolute path to the explorer's config file
        @param resc: a reference to the rescuer agent to invoke when exploration finishes
        """

        super().__init__(env, config_file)                
        Explorer.instance_count += 1
        self.id = Explorer.instance_count  #Unique id for the explorer
        self.walk_stack = Stack()  # a stack to store the movements7
        self.walk_time = 0         # time consumed to walk when exploring (to decide when to come back)
        self.set_state(VS.ACTIVE)  # explorer is active since the begin
        self.resc = resc           # reference to the rescuer agent
        self.x = 0                 # current x position relative to the origin 0
        self.y = 0                 # current y position relative to the origin 0
        self.previous_x = 0        # previous x position relative to the origin 0
        self.previous_y = 0        # previous y position relative to the origin 0
        self.map = Map()           # create a map for representing the environment
        self.victims = {}          # a dictionary of found victims: (seq): ((x,y), [<vs>])
                                   # the key is the seq number of the victim,(x,y) the position, <vs> the list of vital signals
        self.action_order = {
            'N': 0,
            'NE': 1,
            'E': 2,
            'SE': 3,
            'S': 4,
            'SO': 5,
            'W': 6,
            'NO': 7,
        }
        self.backtracked = {}      # dicionario de posicoes anteriores de dada posicao, exemplo {(1,1): [(0,0), (2,2)]}
                                   # nesse caso, (2,2) é a posicao anterior mais recente a (1,1) e deve ser acessada se nao houver
                                   # mais nenhuma direcao nao explorada a partir de (1,1)  
                                   # Aqui usamos pilha para as posicoes anteriores, para fazer LIFO  
        self.untried = {}          # dicionario de direcoes ainda nao exploradas por um posicao (x,y)
                                   # (x,y) , [0, 1, 2, 3, 4, 5, 6, 7]

        if self.id == 1:   #first agent's sequence of actions
            self.actions = ["N","S","E","W","NO","NE","SO","SE"]
        elif self.id == 2: #second agent's sequence of actions
            self.actions = ["N","E","W","S","SO","NE","NO","SE"]
        elif self.id == 3: #third agent's sequence of actions
            self.actions = ["NE","E","S","SO","W","N","NO","SE"]
        else:              #fourth agent's sequence of actions
            self.actions = ["E","W","S","N","SE","SO","NO","NE"]

        self.versao = {
            1: ([2, 4, 6, 0, 3, 5, 1, 7], [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (-1, 1), (-1, -1)]),  
            2: ([0, 2, 4, 6, 3, 5, 7, 1], [(0, -1), (1, 0), (0, 1), (-1, 0), (1, 1), (-1, 1), (-1, -1) , (1, -1)]),  
            3: ([7, 6, 5, 4, 3, 2, 1, 0], [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]),  
            4: ([1, 2, 7, 0, 6, 3, 4, 5], [(1, -1), (1, 0), (-1, -1), (0, -1), (-1, 0), (1, 1), (0, 1), (-1, 1)])   
        }

        if self.id not in self.versao:
            raise ValueError(f"Invalid versao: {self.id}. Valid versions are: {list(self.versao.keys())}")
        self.number, self.indicacao = self.versao[self.id]

        # put the current position - the base - in the map
        self.map.add((self.x, self.y), 1, VS.NO_VICTIM, self.check_walls_and_lim())

        self.stack = [(self.x, self.y)]
        self.visited = set()                           
        self.env = env # it is the environment
        self.start = (self.x,self.y)    # the starting position        
        self.visited_positions = [] # a list of visited positions
        self.visited_victims = [] # a list of visited victims 
        # put the current position - the base - in the map
        self.map.add((self.x, self.y), 1, VS.NO_VICTIM, self.check_walls_and_lim())

    # def get_next_position(self):
    #     # Check the neighborhood walls and grid limits
    #     obstacles = self.check_walls_and_lim()
    
    #     # Loop until a CLEAR position is found
    #     while True:
    #         # Get a direction from the DFS algorithm
    #         direction = self.DFS_online()
    #     # Check if the corresponding position in walls_and_lim is CLEAR
    #         if obstacles[direction] == VS.CLEAR:
    #             return Explorer.AC_INCR[direction]
    
    def get_next_position(self):
        #number=[2,5,7,3,4,6,0,1]
        #indicacao = [(1, 0),(-1, 1),(1, -1),(1, 1), (0, 1),(-1, 0),(-1, -1),(0,-1)]

        currCell = (self.x, self.y)
        if not hasattr(self, 'visited_stack'):
            self.visited_stack = [currCell]
        if currCell not in self.visited:
            self.visited.add(currCell)
        obstacles = self.check_walls_and_lim()

        # Loop until a CLEAR position is found
        for k in range(len(self.number)):
            i = self.number[k]
            dx, dy = self.indicacao[k]
            childcell = (currCell[0] + dx, currCell[1] + dy)

            if obstacles[i] == VS.CLEAR and childcell[0] < self.env.dic["GRID_WIDTH"] and childcell[1] < self.env.dic["GRID_HEIGHT"] and childcell not in self.visited:
                self.visited.add(childcell)
                self.visited_stack.append(childcell)
                return Explorer.AC_INCR[i]

        # If no CLEAR position is found, backtrack to a previously visited position
        if len(self.visited_stack) > 1:
            self.visited_stack.pop()  # Remove current position
            last_visited = self.visited_stack[-1]  # Get last visited position
            return (last_visited[0] - currCell[0], last_visited[1] - currCell[1])  # Return direction to last visited position

        # If no previously visited position is available, return None
        return None
                
    def explore(self):
        # get an random increment for x and y       
        next_position = self.get_next_position()

        # Check if next_position is None
        if next_position is None:
            return  # Exit explore() if no available actions

        # verificar se ja nao visitou essa posicao em MAP ???

        dx, dy = next_position

        # Moves the body to another position
        rtime_bef = self.get_rtime()
        result = self.walk(dx, dy)
        rtime_aft = self.get_rtime()

        # Test the result of the walk action
        # Should never bump, but for safe functioning let's test
        if result == VS.BUMPED:
            # update the map with the wall
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
        pos_atual = (self.x, self.y)
        # Se a posição atual não está no dicionário untried
        if pos_atual not in self.untried:
            # Adiciona a posição atual no untried com suas 8 opções
            self.untried[pos_atual] = list(range(8))

        # transformando as direcoes do agente atual em numberos de 0 a 7
        lista_direcoes_agente = [self.action_order[action] for action in self.actions]

        # Verifica se todas as direções possíveis dessa posição já foram exploradas
        if all(action not in lista_direcoes_agente for action in self.untried.get(pos_atual, [])):
            # Adiciona, para a pilha de backtracked da próxima posição, a posição atual
            proxima_pos = None
            if len(self.backtracked[pos_atual]) > 0:
                proxima_pos = self.backtracked[pos_atual].pop()

            if proxima_pos is not None: 
                if proxima_pos != pos_anterior:
                    # garante que nao entrou em loop
                    if pos_atual in self.backtracked:
                        self.backtracked[proxima_pos].append(pos_atual)
                    else:
                        self.backtracked[proxima_pos] = [pos_atual]

                    direction = self.calcular_direcao(pos_atual, proxima_pos)
                    return direction
            
            # se entrar em loop, sorteia outra posicao
            return random.randint(0, 7)

        else:
            # Verifica qual a ordem de direções desse agente e pega a primeira que der match no array
            # correspondente da posição atual do dicionário
            for direcao in lista_direcoes_agente:
                if direcao in self.untried[pos_atual]:
                    # Retira esse valor das direções para essa posição     
                    self.untried[pos_atual].remove(direcao)

                    # Caso não seja a primeira execução
                    if pos_anterior is not None:
                        # Adiciona a posição anterior na pilha de backtracked:
                        # Verifica se a posição atual existe no dicionário backtracked
                        if pos_atual in self.backtracked:
                            # Adiciona a pos_anterior ao array associado à chave pos_atual
                            self.backtracked[pos_atual].append(pos_anterior)
                        else:
                            # Se pos_atual não existir no dicionário, cria uma nova entrada com pos_anterior como o único elemento da lista
                            self.backtracked[pos_atual] = [pos_anterior]

                    # Retorna a direção
                    return direcao


    
    def calcular_direcao(self, base, target):   
        # auxiliar para DFS online
        x_base, y_base = base
        x_target, y_target = target

        diff_x = x_target - x_base
        diff_y = y_target - y_base

        if diff_y == 0:
            if diff_x == 1:
                return 2
            elif diff_x == -1:
                return 6
        elif diff_x == 0:
            if diff_y == 1:
                return 0
            elif diff_y == -1:
                return 4
        elif diff_y == 1:
            if diff_x == 1:
                return 1
            elif diff_x == -1:
                return 7
        elif diff_y == -1:
            if diff_x == 1:
                return 3
            elif diff_x == -1:
                return 5
    
    # def deliberate(self) -> bool:
    #     """ The agent chooses the next action. The simulator calls this
    #     method at each cycle. Must be implemented in every agent"""

    #     consumed_time = self.TLIM - self.get_rtime()
    #     if consumed_time < self.get_rtime():
    #         self.explore()
    #         return True

    #     # time to come back to the base
    #     if self.walk_stack.is_empty() or (self.x == 0 and self.y == 0):
    #         # time to wake up the rescuer
    #         # pass the walls and the victims (here, they're empty)
    #         print(f"{self.NAME}: rtime {self.get_rtime()}, invoking the rescuer")
    #         #input(f"{self.NAME}: type [ENTER] to proceed")
    #         self.resc.go_save_victims(self.map, self.victims)
    #         return False

    #     return self.come_back_with_astar()

    def deliberate(self) -> bool:
        """ The agent chooses the next action. The simulator calls this
        method at each cycle. Must be implemented in every agent"""

        # forth and back: go, read the vital signals and come back to the position

        time_tolerance = 2* self.COST_DIAG * Explorer.MAX_DIFFICULTY + self.COST_READ

        # keeps exploring while there is enough time
        if self.walk_time < (self.get_rtime() - time_tolerance):
            self.explore()

        # no more come back walk actions to execute or already at base
        if self.walk_stack.is_empty() or (self.x == 0 and self.y == 0):
            # time to pass the map and found victims to the master rescuer
            self.resc.sync_explorers(self.map, self.victims)
            # finishes the execution of this agent
            return False
        else:
            if self.get_rtime() <= self.TLIM / 2:
                # proceed to the base
                self.come_back_with_astar()
                return True
            return True
        
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
        self.walk_stack.pop()
        # monta grafo com as posicoes exploradas (o mapa) usando matriz de adjacencias
        adjacency_matrix = self.build_adjacency_matrix()

        # Uso do A* para achar o caminho mais curto de volta
        shortest_path = self.find_shortest_path(adjacency_matrix, (self.x, self.y), (0, 0))
        
        # Verificar se o caminho foi encontrado
        if len(shortest_path) >= 2:
            # O próximo movimento será a próxima posição no caminho mais curto
            next_position = shortest_path[1]  # A primeira posição é a atual
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