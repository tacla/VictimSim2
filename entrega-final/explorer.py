# EXPLORER AGENT
# @Author: Tacla, UTFPR
#
### Este agente explora o ambiente procurando por vítimas. Quando metade do
### tempo de exploração se esgota, ele tenta voltar para a base.

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
    """ O agente Explorer realiza exploração do ambiente procurando vítimas.
        Quando metade do tempo de exploração passa, tenta retornar à base.
    """
    MAX_DIFFICULTY = 3  # dificuldade máxima para entrar numa célula

    def __init__(self, env, config_file, resc):
        """
        Construtor do agente explorer.
        @param env: referência ao ambiente
        @param config_file: caminho absoluto do arquivo de configuração do explorer
        @param resc: referência ao agente rescuer para ser invocado quando a exploração terminar
        """
        super().__init__(env, config_file)

        # Armazena a posição obtida de acordo com o movimento realizado
        self.dfs_moveResults = {}

        # Dicionário para movimentos de backtracking
        self.unbacktracked = {}

        # Movimentos não tentados para determinada posição
        self.untried_move_by_pos = {}

        # Agora usamos uma lista para armazenar o caminho de volta, já que precisamos indexar
        self.come_back_path = []  # era Stack() anteriormente

        self.is_unbacktracking = False
        self.flag_explore = True
        self.last_position = None
        self.last_movement = None

        self.walk_time = 0
        self.set_state(VS.ACTIVE)
        self.resc = resc

        self.x = 0
        self.y = 0
        self.map = Map()
        self.victims = {}

        # Adiciona a posição atual (a base) no mapa
        self.map.add((self.x, self.y), 1, VS.NO_VICTIM, self.check_walls_and_lim())

    def search_key(self, d, position, target):
        """Busca uma chave em d onde 'position' está na chave (tupla) e o valor == target."""
        for key, value in d.items():
            if position in key and value == target:
                return key
        return None

    def actions(self, position):
        """
        Define as ações possíveis para o explorer e suas prioridades, 
        baseadas no nome do explorer e no tempo de caminhada.
        """
        simple_moves = [0, 2, 4, 6]
        diagonal_moves = [1, 3, 5, 7]

        # Ordens pré-definidas para cada explorer visando um canto do mapa (por exemplo)
        orderToCorner = {
            "EXPL_1": [0, 2, 4, 1, 3, 7, 6, 5],
            "EXPL_2": [4, 2, 0, 3, 1, 5, 6, 7],
            "EXPL_3": [4, 6, 0, 5, 1, 3, 2, 7],
            "EXPL_4": [0, 6, 4, 1, 5, 7, 2, 3],
        }

        if self.walk_time <= self.TLIM * 0.4:
            order = orderToCorner.get(self.NAME, list(self.AC_INCR.keys()))
        else:
            # Se já passou 40% do tempo, embaralha as ordens
            random.shuffle(simple_moves)
            random.shuffle(diagonal_moves)
            order = simple_moves + diagonal_moves
        
        if position in self.untried_move_by_pos:
            # Ordena as ações não tentadas de acordo com a ordem definida
            return sorted(self.untried_move_by_pos[position], key=lambda x: order.index(x))
        else:
            return order

    def add_unbacktracked(self, position):
        """Adiciona a última posição à pilha de backtracking de 'position' se necessário."""
        if self.last_position != position:
            if position not in self.unbacktracked:
                self.unbacktracked[position] = [self.last_position]
            else:
                self.unbacktracked[position].insert(0, self.last_position)

    def manhattan_distance(self, position):
        """Calcula a distância de manhattan da origem."""
        return abs(position[0]) + abs(position[1]) * 1.5

    def online_dfs(self, position):
        """Realiza um DFS online para decidir o próximo movimento."""
        if position not in self.untried_move_by_pos:
            self.untried_move_by_pos[position] = self.actions(position)

        # Se mudou de posição e não está em backtracking, adiciona para possível backtrack
        if self.last_position is not None and self.last_position != position:
            self.dfs_moveResults[(self.last_position, self.last_movement)] = position
            if not self.is_unbacktracking:
                self.add_unbacktracked(position)

        # Se não há mais movimentos não tentados na posição atual
        if len(self.untried_move_by_pos[position]) == 0:
            # Verifica o backtracking
            if position not in self.unbacktracked or len(self.unbacktracked[position]) == 0:
                # Sem movimentos para tentar ou para voltar
                return -1
            else:
                unback_pos = self.unbacktracked[position][0]
                del(self.unbacktracked[position][0])
                self.is_unbacktracking = True
                k = self.search_key(self.dfs_moveResults, position, unback_pos)
                if k is not None:
                    self.last_movement = k[1]
                else:
                    self.last_movement = -1
        else:
            # Ainda há movimentos não tentados
            self.is_unbacktracking = False
            self.last_movement = self.untried_move_by_pos[position][0]
            del(self.untried_move_by_pos[position][0])

        self.last_position = position
        return self.last_movement

    def reconstruct_path(self, came_from, current):
        """Reconstrói o caminho resultado do A*."""
        total_path = [current]
        while current in came_from.keys():
            current = came_from[current]
            total_path.append(current)
        return total_path

    def return_neighbors(self, position):
        """Retorna vizinhos válidos da posição, considerando limites do mapa."""
        neighbors = []
        for i in range(-1,2):
            for j in range(-1,2):
                neighbor = (position[0]+i, position[1]+j)
                if self.map.in_map(neighbor) and neighbor != position:
                    neighbors.append(neighbor)
        return neighbors

    def a_star(self, cur_Position, goal):
        """Busca A* para encontrar um caminho de cur_Position até goal."""
        open_set = {cur_Position}
        came_from = {}
        g_score = {}
        f_score = {}
        
        for e in self.map.data:
            g_score[e] = math.inf
            f_score[e] = math.inf
        
        g_score[cur_Position] = 0
        f_score[cur_Position] = self.manhattan_distance(cur_Position)

        while len(open_set) != 0:
            value = math.inf
            for e in open_set:
                if f_score[e] < value:
                    current = e
                    value = f_score[e]

            if current == goal:
                return self.reconstruct_path(came_from, current)

            open_set.remove(current)
            for neighbor in self.return_neighbors(current):
                tentative_gscore = g_score[current] + self.map.get_difficulty(neighbor)
                if tentative_gscore < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_gscore
                    f_score[neighbor] = tentative_gscore + self.manhattan_distance(neighbor)
                    if neighbor not in open_set:
                        open_set.add(neighbor)
        print('Erro!')
        return EOFError

    def get_next_position(self):
        """
        Obtém a próxima posição a ser explorada, garantindo que seja uma célula livre (CLEAR).
        Caso não haja movimentos possíveis, retorna (0,0).
        """
        obstacles = self.check_walls_and_lim()
        while True:
            movement = self.online_dfs((self.x, self.y))
            if movement == -1:
                return (0,0)
            if not isinstance(movement, int):
                # Caso de debug
                print("DEBUG: movement is not int:", movement)
                return (0,0)
            if obstacles[movement] == VS.CLEAR:
                return Explorer.AC_INCR[movement]

    def explore(self):
        """Explora o ambiente enquanto há tempo."""
        dx, dy = self.get_next_position()
        if (dx, dy) == (0,0):
            # Sem movimentos possíveis
            return

        rtime_bef = self.get_rtime()
        result = self.walk(dx, dy)
        rtime_aft = self.get_rtime()

        # Se houve colisão (improvável, mas tratado)
        if result == VS.BUMPED:
            self.map.add((self.x + dx, self.y + dy), VS.OBST_WALL, VS.NO_VICTIM, self.check_walls_and_lim())

        if result == VS.EXECUTED:
            self.x += dx
            self.y += dy
            self.walk_time += (rtime_bef - rtime_aft)

            seq = self.check_for_victim()
            if seq != VS.NO_VICTIM:
                vs = self.read_vital_signals()
                self.victims[vs[0]] = ((self.x, self.y), vs)

            difficulty = (rtime_bef - rtime_aft)
            if dx == 0 or dy == 0:
                difficulty = difficulty / self.COST_LINE
            else:
                difficulty = difficulty / self.COST_DIAG

            self.map.add((self.x, self.y), difficulty, seq, self.check_walls_and_lim())
        return

    def come_back(self):
        """Tenta retornar à base (0,0) quando o tempo de exploração acaba."""
        # Se ainda estava explorando, calcula o caminho de volta
        if self.flag_explore:
            path = self.a_star((self.x, self.y), (0,0))
            # Se não há caminho (EOFError), poderia tratar aqui se necessário
            if path == EOFError:
                # Caso não seja possível encontrar caminho, encerra ou toma alguma decisão
                # Por ora, apenas não atualiza o come_back_path
                return
            else:
                self.come_back_path = path
                self.flag_explore = False

        # Se ainda há posições no caminho de volta
        if len(self.come_back_path) > 1:
            dx = self.come_back_path[-2][0] - self.come_back_path[-1][0]
            dy = self.come_back_path[-2][1] - self.come_back_path[-1][1]
            self.come_back_path.pop()
        else:
            dx, dy = self.come_back_path.pop()

        result = self.walk(dx, dy)
        if result == VS.BUMPED:
            print(f"{self.NAME}: when coming back bumped at ({self.x+dx}, {self.y+dy}) , rtime: {self.get_rtime()}")
            return
        
        if result == VS.EXECUTED:
            self.x += dx
            self.y += dy
            print(f"{self.NAME}: coming back at ({self.x}, {self.y}), rtime: {self.get_rtime()}")


    def deliberate(self) -> bool:
        """
        O agente escolhe a próxima ação. O simulador chama este método a cada ciclo.

        @return True se há mais ações a fazer, False caso contrário
        """
        additional_safety_margin = 30
        estimated_return_cost = self.manhattan_distance((self.x, self.y)) * self.COST_LINE
        time_tolerance = 2 * self.COST_DIAG * Explorer.MAX_DIFFICULTY + self.COST_READ + additional_safety_margin

        # Continua explorando enquanto houver tempo seguro
        if self.flag_explore and self.get_rtime() > (estimated_return_cost + time_tolerance):
            self.explore()
            return True

        # Se chegou à base, sincroniza com o rescuer e finaliza
        if (self.x == 0 and self.y == 0):
            self.resc.sync_explorers(self.map, self.victims)
            return False

        # Caso contrário, tenta voltar à base
        self.come_back()
        return True
