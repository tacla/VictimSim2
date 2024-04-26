# RESCUER AGENT
# @Author: Tacla (UTFPR)
# Demo of use of VictimSim
# Not a complete version of DFS; it comes back prematuraly
# to the base when it enters into a dead end position


import os
import random
from map import Map
from vs.abstract_agent import AbstAgent
from vs.physical_agent import PhysAgent
from vs.constants import VS
from abc import ABC, abstractmethod
import numpy as np
from python_tsp.distances import great_circle_distance_matrix
from python_tsp.exact import solve_tsp_dynamic_programming
import math
import random
from astar_algorithm import AStarExplorer


# Classe que define o Agente Rescuer com um plano fixo
class Rescuer(AbstAgent):
    def __init__(self, env, config_file, rescuer_id):
        """ 
        @param env: a reference to an instance of the environment class
        @param config_file: the absolute path to the agent's config file"""

        super().__init__(env, config_file)

        # Specific initialization for the rescuer
        self.map = None             # explorer will pass the map
        self.victims = None         # list of found victims
        self.plan = []              # a list of planned actions
        self.plan_x = 0             # the x position of the rescuer during the planning phase
        self.plan_y = 0             # the y position of the rescuer during the planning phase
        self.plan_visited = set()   # positions already planned to be visited
        self.plan_rtime = self.TLIM  # the remaing time during the planning phase
        self.plan_walk_time = 0.0   # previewed time to walk during rescue
        self.x = 0                  # the current x position of the rescuer when executing the plan
        self.y = 0                  # the current y position of the rescuer when executing the plan

        self.sequences = []   # the sequence of visit of victims for each cluster

        # Starts in IDLE state.
        # It changes to ACTIVE when the map arrives
        self.set_state(VS.IDLE)

        self.id = rescuer_id
        self.victims_to_be_saved = []

    def go_save_victims(self, map, victims):
        """ The explorer sends the map containing the walls and
        victims' location. The rescuer becomes ACTIVE. From now,
        the deliberate method is called by the environment"""

        print(f"\n\n*** R E S C U E R ***")
        self.map = map
        print(f"{self.NAME} Map received from the explorer")
        self.map.draw()

        # print(f"{self.NAME} List of found victims received from the explorer")
        self.victims = victims

        # print the found victims - you may comment out
        # for seq, data in self.victims.items():
        #    coord, vital_signals = data
        #    x, y = coord
        #    print(f"{self.NAME} Victim seq number: {seq} at ({x}, {y}) vs: {vital_signals}")

        # print(f"{self.NAME} time limit to rescue {self.plan_rtime}")

        self.__planner()
        print(f"{self.NAME} PLAN")
        i = 1
        self.plan_x = 0
        self.plan_y = 0
        for a in self.plan:
            self.plan_x += a[0]
            self.plan_y += a[1]
            print(
                f"{self.NAME} {i}) dxy=({a[0]}, {a[1]}) vic: a[2] => at({self.plan_x}, {self.plan_y})")
            i += 1

        print(f"{self.NAME} END OF PLAN")

        self.set_state(VS.ACTIVE)

        print("🤖 Inicio do sequenciamento:")
        print()
        victims_info_array = [[1, (4, 2), 0], [2, (0, 0), 1], [3, (1, 5), 2],  [
            4, (3, 3), 3], [5, (4, 2), 3], [6, (4, 2), 2], [7, (4, 2), 1]]
        self.sequences = self.sequencia(victims_info_array, [], [], [], 0)
        #self.sequences = self.sequencia(self.victims_to_be_saved, [], [], [], 0)
        print("🤖 Fim do sequenciamento, rota de salvamento:")
        print(self.sequences)
        print()
        # Salva a sequencia de salvamento desse agente num .txt
        self.save_sequence_csv(self.id, self.sequences)

    # num: o numero do rescuer, de 1 a 4
    # sequence: a sequencia de salvamento das vitimas, um array de arrays
    def save_sequence_csv(self, num, sequence):
        with open(f'seq_{num}.txt', 'w') as file:
            # Escrevendo o cabeçalho
            file.write("id, x, y, grav, classe\n")

            # Iterando sobre as informações das vítimas
            for info in sequence:
                # Extrair informações
                id_vitima = info[0]
                posicao = info[1]
                gravidade = info[2]

                # Determinar classe com base na gravidade
                classe = self.determinar_classe(gravidade)

                # Escrever no arquivo
                file.write(
                    f"{id_vitima}, {posicao[0]}, {posicao[1]}, {gravidade}, {classe}\n")

    # Função para determinar a classe com base na gravidade
    def determinar_classe(self, gravidade):
        if gravidade == 0:
            return "estável"
        elif gravidade == 1:
            return "potencialmente estável"
        elif gravidade == 2:
            return "instável"
        elif gravidade == 3:
            return "crítico"
        else:
            return "desconhecido"

    def __depth_search(self, actions_res):
        enough_time = True
        # print(f"\n{self.NAME} actions results: {actions_res}")
        for i, ar in enumerate(actions_res):

            if ar != VS.CLEAR:
                # print(f"{self.NAME} {i} not clear")
                continue

            # planning the walk
            # get the increments for the possible action
            dx, dy = Rescuer.AC_INCR[i]
            target_xy = (self.plan_x + dx, self.plan_y + dy)

            # checks if the explorer has not visited the target position
            if not self.map.in_map(target_xy):
                # print(f"{self.NAME} target position not explored: {target_xy}")
                continue

            # checks if the target position is already planned to be visited
            if (target_xy in self.plan_visited):
                # print(f"{self.NAME} target position already visited: {target_xy}")
                continue

            # Now, the rescuer can plan to walk to the target position
            self.plan_x += dx
            self.plan_y += dy
            difficulty, vic_seq, next_actions_res = self.map.get(
                (self.plan_x, self.plan_y))
            # print(f"{self.NAME}: planning to go to ({self.plan_x}, {self.plan_y})")

            if dx == 0 or dy == 0:
                step_cost = self.COST_LINE * difficulty
            else:
                step_cost = self.COST_DIAG * difficulty

            # print(f"{self.NAME}: difficulty {difficulty}, step cost {step_cost}")
            # print(f"{self.NAME}: accumulated walk time {self.plan_walk_time}, rtime {self.plan_rtime}")

            # check if there is enough remaining time to walk back to the base
            if self.plan_walk_time + step_cost > self.plan_rtime:
                enough_time = False
                # print(f"{self.NAME}: no enough time to go to ({self.plan_x}, {self.plan_y})")

            if enough_time:
                # the rescuer has time to go to the next position: update walk time and remaining time
                self.plan_walk_time += step_cost
                self.plan_rtime -= step_cost
                self.plan_visited.add((self.plan_x, self.plan_y))

                if vic_seq == VS.NO_VICTIM:
                    self.plan.append((dx, dy, False))  # walk only
                    # print(f"{self.NAME}: added to the plan, walk to ({self.plan_x}, {self.plan_y}, False)")

                if vic_seq != VS.NO_VICTIM:
                    # checks if there is enough remaining time to rescue the victim and come back to the base
                    if self.plan_rtime - self.COST_FIRST_AID < self.plan_walk_time:
                        print(f"{self.NAME}: no enough time to rescue the victim")
                        enough_time = False
                    else:
                        self.plan.append((dx, dy, True))
                        # print(f"{self.NAME}:added to the plan, walk to and rescue victim({self.plan_x}, {self.plan_y}, True)")
                        self.plan_rtime -= self.COST_FIRST_AID

            # let's see what the agent can do in the next position
            if enough_time:
                self.__depth_search(self.map.get((self.plan_x, self.plan_y))[
                                    2])  # actions results
            else:
                return

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

        # always start from the base, so it is already visited
        self.plan_visited.add((0, 0))
        difficulty, vic_seq, actions_res = self.map.get((0, 0))
        self.__depth_search(actions_res)

        # push actions into the plan to come back to the base
        if self.plan == []:
            return

        come_back_plan = []

        for a in reversed(self.plan):
            # triple: dx, dy, no victim - when coming back do not rescue any victim
            come_back_plan.append((a[0]*-1, a[1]*-1, False))

        self.plan = self.plan + come_back_plan

# *************
#  Traveling salesman and genetic algorithm
# *************

# COMO USAR
#
# Mandar o array de vitimas para ser sequenciado da seguinte maneira exemplo:
# victims_info_array = [ [1, (4,2), 0], [2, (0,0), 1], [3, (1,5), 2],  [4, (3,3), 3], [5, (4,2), 0], [6, (4,2), 2], [7, (4,2), 3] ]
# Parametros:
# [id_vitima, pos, gravidade_vitima], entao para a primeira vitima, temos id_vitima = 1, pos = (4,2), gravidade = 0
#
# Para chamar o método que fará o sequenciamento:
# rota_final = self.sequencia(victims_info_array, [], [], [], 0)
#
# ******

    # Populacao inicial: Gerando uma população inicial de soluções (permutações) de maneira aleatória
    # Gera quatro permutacoes de rotas usando o caixeiro viajante. Ou seja, quatro individuos
    # da populacao, sendo que cada individuo represente uma ordem de salvamento das vitimas (uma rota)
    # Embaralha aleatoriamente a lista original de vitimas, gerando novas sequencias de salvamento
    def populacao_inicial(self, victims_info_inicial):
        lista_1 = random.sample(victims_info_inicial,
                                len(victims_info_inicial))
        lista_2 = random.sample(victims_info_inicial,
                                len(victims_info_inicial))
        lista_3 = random.sample(victims_info_inicial,
                                len(victims_info_inicial))
        lista_4 = random.sample(victims_info_inicial,
                                len(victims_info_inicial))

        return lista_1, lista_2, lista_3, lista_4

    # Funcao auxiliar: Calcula a gravidade ponderada de uma rota:
    # Para todos os itens: multiplica o inverso da posicao no array, pela gravidade dessa posicao
    # Assim, arrays que tiverem ordenados de maior a menor gravidade, terão uma gravidade ponderada (score) maior
    # rota: recebe um array de arrays, onde:
    #  o primeiro item é o id da vitima
    #  o segundo item é a posicao da vitima
    #  o terceiro item é a gravidade da vitima
    def calcular_gravidades_ponderadas(self, rota):
        gravidades_ponderadas = []
        for idx, info in enumerate(rota):
            gravidade = info[2]
            gravidade_ponderada = (1 / (idx + 1)) * gravidade
            gravidades_ponderadas.append(gravidade_ponderada)
        return gravidades_ponderadas

    # Funcao auxiliar: calcula o tempo de deslocamento entre dois pontos no mapa
    def tempo_deslocamento(self, pos1, pos2):
        # Uso do A* para determinar a distancia entre dois pontos
        adjacency_matrix = self.build_adjacency_matrix()
        shortest_path = self.find_shortest_path(adjacency_matrix, pos1, pos2)
        tamanho = len(shortest_path)

        return tamanho

    def find_shortest_path(self, graph, start, goal):
        astar = AStarExplorer(graph, start, goal,
                              self.COST_DIAG, self.COST_LINE, self.map)
        path = list(astar.find_path())
        return path

    # Retorna um objeto adjacency_matrix[i][j], que vale 1 se há uma aresta entre os vértices i e j, e 0 caso contrário.
    # Cada vértice na matriz corresponde a uma posição visitada pelo agente no mapa.
    def build_adjacency_matrix(self):
        adjacency_matrix = [[0] * len(self.map.map_data)
                            for _ in range(len(self.map.map_data))]

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
                            adjacency_matrix[coord_to_index[coord]
                                             ][coord_to_index[neighbor_coord]] = 1

        return adjacency_matrix

    # Função de aptidão
    # Avalia quão boa é uma solução, gerada com o caixeiro viajante, tendo como entrada uma possivel rota
    # permutacao: recebe um array de arrays, onde
    #  o primeiro item é o id da vitima
    #  o segundo item é a posicao da vitima
    #  o terceiro item é a gravidade da vitima
    def aptidao(self, permutacao):
        gravidade_ponderada = self.calcular_gravidades_ponderadas(permutacao)
        soma_gravidade_ponderada = sum(gravidade_ponderada)

        pos_atual = self.x, self.y
        distancia_total = 0
        for posicoes in permutacao:
            proxima_pos = posicoes[1]  # pega posicao da vitima
            # tempo para ir da posicao atual ate a proxima vitima
            distancia = self.tempo_deslocamento(pos_atual, proxima_pos)
            distancia_total += distancia
            pos_atual = proxima_pos

        # O score deve ser maior quanto maior a gravidade ponderada, e menor a distancia que precisa ser percorrida
        return soma_gravidade_ponderada + (1/distancia_total)

    # Considera só a gravidade e nao as distancias

    def aptidao_v2(self, permutacao):
        gravidade_ponderada = self.calcular_gravidades_ponderadas(permutacao)
        soma_gravidade_ponderada = sum(gravidade_ponderada)

        # O score deve ser maior quanto maior a gravidade ponderada
        return soma_gravidade_ponderada

    # Mutação:
    # Aplica operadores de mutação para introduzir diversidade na população. Faz isso trocando duas posicoes de uma rota
    def mutate(self, route):
        # Escolher aleatoriamente dois índices distintos na lista
        idx1, idx2 = random.sample(range(len(route)), 2)
        # Trocar os elementos nos índices selecionados
        route[idx1], route[idx2] = route[idx2], route[idx1]
        return route

    # Recombinação (Crossover):
    # Aplica operadores de crossover (recombinação) para criar novos indivíduos (soluções).
    def crossover(self, route1, route2):
        # Escolher um ponto de corte aleatório
        crossover_point = random.randint(1, len(route1) - 1)
        # Trocar as subsequências das rotas a partir do ponto de corte
        new_route1 = route1[:crossover_point] + \
            [pos for pos in route2 if pos not in route1[:crossover_point]]
        new_route2 = route2[:crossover_point] + \
            [pos for pos in route1 if pos not in route2[:crossover_point]]

        return new_route1, new_route2

    # Funcao auxiliar: usada para retornar uma lista de prioridades de posicoes, para uma lista de posicoes
    # exemplo:
    # list = [(0, 0), (1,2), (3,0), (6, 7)]
    # permutation = [0, 3, 1, 2]
    # return = [(0,0), (6,7),(1,2),(3,0)]
    def convert_to_position(self, positions, permutation):
        return [positions[i] for i in permutation]

    # Funçoes aulixiares do algoritmo escolhido: Caixeiro viajante
    # gera a matriz de distancias
    def calculate_distance(self, pos1, pos2):
        x1, y1 = pos1
        x2, y2 = pos2
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def generate_distance_matrix(self, victims_info):
        positions = [info[1] for info in victims_info]
        n = len(positions)
        distance_matrix = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                distance_matrix[i][j] = self.calculate_distance(
                    positions[i], positions[j])
        return distance_matrix

    # melhor_lista: parametro obrigatorio
    # na primeira chamada da funcao deve ser o grupo inicial de vitimas
    # nas demais, a propria funcao irá se chamar com a melhor lista ate entao
    def sequencia(self, melhor_lista, segunda_lista, terceira_lista, quarta_lista, iteracoes_geneticas):
        if iteracoes_geneticas == 0:
            # Passo 1: Populacao inicial
            lista_1, lista_2, lista_3, lista_4 = self.populacao_inicial(
                melhor_lista)
        elif iteracoes_geneticas >= 20:
            # TODO: Colocar numero do criterio de parada numa variavel separada
            # Passo final: criterio de parada
            return melhor_lista
        else:
            # já iterei alguma vez e já possuo 4 individuos na populacao
            lista_1, lista_2, lista_3, lista_4 = melhor_lista, segunda_lista, terceira_lista, quarta_lista

        print("primeira selecao")
        # Passo 2: Seleção
        # Seleciona 2 melhores indivíduos da população atual para reprodução
        all_lists = [lista_1, lista_2, lista_3, lista_4]
        melhor_pontuacao = 1
        melhor_rota = lista_1
        segunda_melhor_pontuacao = 0
        segunda_melhor_rota = lista_2

        for i, lista in enumerate(all_lists):
            distance_matrix = self.generate_distance_matrix(lista)
            distance_matrix = np.array(distance_matrix)
            permutation, distance = solve_tsp_dynamic_programming(
                distance_matrix)

            print("🧾 {}ª lista sendo avaliada para selecao:".format(i+1))
            permutation = self.convert_to_position(lista, permutation)
            print("Lista: {}".format(permutation))

            # Passo 3: Usar a funcao de aptidao para cumprir o passo 2
            pontuacao_rota_atual = self.aptidao(permutation)
            print("Pontuacao:", pontuacao_rota_atual)
            if pontuacao_rota_atual > melhor_pontuacao:
                melhor_pontuacao = pontuacao_rota_atual
                melhor_rota = permutation
                melhor_distancia = distance
            else:
                if pontuacao_rota_atual > segunda_melhor_pontuacao:
                    segunda_melhor_pontuacao = pontuacao_rota_atual
                    segunda_melhor_rota = permutation
                    segunda_melhor_distancia = distance

        print("🌳 Melhores rotas (individuos) pós seleção:")
        print("Pai 1:", melhor_rota)
        print("Pai 2:", segunda_melhor_rota)

        # Passo 4: Recombinação (Crossover):
        # Vamos usar os dois melhores individuos, gerados na ultima etapa, para criar mais dois
        nova_rota1, nova_rota2 = self.crossover(
            melhor_rota, segunda_melhor_rota)
        print("🍓 Dois novos individuos pós crossover:")
        print("Nova Rota 1:", nova_rota1)
        print("Nova Rota 2:", nova_rota2)

        # Passo 5: Mutação:
        # Gera uma mutação aleatória em um dos indivíduos da população
        nova_rota1 = self.mutate(nova_rota1)
        print("Inidividuo nova_rota_1 mutado, pós mutação:", nova_rota1)

        print("Fim da {} iteracao".format(iteracoes_geneticas+1))
        print()

        iteracoes_geneticas += 1
        # Loop até que seja atingido o critério de parada
        return self.sequencia(melhor_rota, segunda_melhor_rota, nova_rota1, nova_rota2, iteracoes_geneticas)

# *********************************
#  Deliberate

    def deliberate(self) -> bool:
        """ This is the choice of the next action. The simulator calls this
        method at each reasonning cycle if the agent is ACTIVE.
        Must be implemented in every agent
        @return True: there's one or more actions to do
        @return False: there's no more action to do """

        # No more actions to do
        if self.plan == []:  # empty list, no more actions to do
            # input(f"{self.NAME} has finished the plan [ENTER]")
            return False

        # Takes the first action of the plan (walk action) and removes it from the plan
        dx, dy, there_is_vict = self.plan.pop(0)
        # print(f"{self.NAME} pop dx: {dx} dy: {dy} vict: {there_is_vict}")

        # Walk - just one step per deliberation
        walked = self.walk(dx, dy)

        # Rescue the victim at the current position
        if walked == VS.EXECUTED:
            self.x += dx
            self.y += dy
            # print(f"{self.NAME} Walk ok - Rescuer at position ({self.x}, {self.y})")
            # check if there is a victim at the current position
            if there_is_vict:
                rescued = self.first_aid()  # True when rescued
                if rescued:
                    print(f"{self.NAME} Victim rescued at ({self.x}, {self.y})")
                else:
                    print(
                        f"{self.NAME} Plan fail - victim not found at ({self.x}, {self.x})")
        else:
            print(
                f"{self.NAME} Plan fail - walk error - agent at ({self.x}, {self.x})")

        # input(f"{self.NAME} remaining time: {self.get_rtime()} Tecle enter")

        return True
