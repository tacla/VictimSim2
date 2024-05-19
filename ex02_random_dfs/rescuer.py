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
import csv
import sys
from classifier import Classifier
from regressor import Regressor
from fitnessRN import fitnessRN
from cluster import Cluster
from bfs import BFS

## Classe que define o Agente Rescuer com um plano fixo
class Rescuer(AbstAgent):
    def __init__(self, env, config_file, config_folder, nb_of_explorers=1,clusters=[]):
        """ 
        @param env: a reference to an instance of the environment class
        @param config_file: the absolute path to the agent's config file
        @param nb_of_explorers: number of explorer agents to wait for
        @param clusters: list of clusters of victims in the charge of this agent"""

        super().__init__(env, config_file)

        # Specific initialization for the rescuer
        self.nb_of_explorers = nb_of_explorers       # number of explorer agents to wait for start
        self.received_maps = 0                       # counts the number of explorers' maps
        self.map = Map()                             # explorer will pass the map
        self.victims = {}            # a dictionary of found victims: [vic_id]: ((x,y), [<vs>])
        self.plan = []               # a list of planned actions in increments of x and y
        self.plan_x = 0              # the x position of the rescuer during the planning phase
        self.plan_y = 0              # the y position of the rescuer during the planning phase
        self.plan_visited = set()    # positions already planned to be visited 
        self.plan_rtime = self.TLIM  # the remaing time during the planning phase
        self.plan_walk_time = 0.0    # previewed time to walk during rescue
        self.x = 0                   # the current x position of the rescuer when executing the plan
        self.y = 0                   # the current y position of the rescuer when executing the plan
        self.clusters = clusters     # the clusters of victims this agent should take care of - see the method cluster_victims
        self.sequences = []    # the sequence of visit of victims for each cluster 
        self.config_folder = config_folder
        self.env = env
        
                
        # Starts in IDLE state.
        # It changes to ACTIVE when the map arrives
        self.set_state(VS.IDLE)

    def save_cluster_csv(self, df, cluster_id):
        filename = f"clusters/cluster{cluster_id}.txt"
        with open(os.path.join("ex02_random_dfs", filename), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for i in range(len(df)):
                id = df.loc[i,'id'] 
                x = df.loc[i,'x']      # x coordinate
                y = df.loc[i,'y']      # y coordinate
                grav = df.loc[i,'grav']
                classe = df.loc[i,'classe']
                writer.writerow([id, x, y, grav, classe])

    def cluster_victims(self):
        """ this method does a naive clustering of victims per quadrant: victims in the
            upper left quadrant compose a cluster, victims in the upper right quadrant, another one, and so on.
            
            @returns: a list of clusters where each cluster is a dictionary in the format [vic_id]: ((x,y), [<vs>])
                      such as vic_id is the victim id, (x,y) is the victim's position, and [<vs>] the list of vital signals
                      including the severity value and the corresponding label"""


        # Find the upper and lower limits for x and y
        lower_xlim = sys.maxsize    
        lower_ylim = sys.maxsize
        upper_xlim = -sys.maxsize - 1
        upper_ylim = -sys.maxsize - 1

        vic = self.victims
    
        for key, values in self.victims.items():
            x, y = values[0]
            lower_xlim = min(lower_xlim, x) 
            upper_xlim = max(upper_xlim, x)
            lower_ylim = min(lower_ylim, y)
            upper_ylim = max(upper_ylim, y)
        
        # Calculate midpoints
        mid_x = lower_xlim + (upper_xlim - lower_xlim) / 2
        mid_y = lower_ylim + (upper_ylim - lower_ylim) / 2
        print(f"{self.NAME} ({lower_xlim}, {lower_ylim}) - ({upper_xlim}, {upper_ylim})")
        print(f"{self.NAME} cluster mid_x, mid_y = {mid_x}, {mid_y}")
    
        # Divide dictionary into quadrants
        upper_left = {}
        upper_right = {}
        lower_left = {}
        lower_right = {}
        
        for key, values in self.victims.items():  # values are pairs: ((x,y), [<vital signals list>])
            x, y = values[0]
            if x <= mid_x:
                if y <= mid_y:
                    upper_left[key] = values
                else:
                    lower_left[key] = values
            else:
                if y <= mid_y:
                    upper_right[key] = values
                else:
                    lower_right[key] = values
    
        return [upper_left, upper_right, lower_left, lower_right]

    def predict_severity_and_class(self):
        """ @TODO to be replaced by a classifier and a regressor to calculate the class of severity and the severity values.
            This method should add the vital signals(vs) of the self.victims dictionary with these two values.

            This implementation assigns random values to both, severity value and class"""
        # Classification
        classifier = Classifier(self.victims)
        self.victims = classifier.make_prediction()
        #for vic_id, values in self.victims.items():    
            #severity_value = random.uniform(0.1, 99.9)          # to be replaced by a regressor 
            #severity_class = random.randint(1, 4)               # to be replaced by a classifier
            #values[1].extend([severity_class])  # append to the list of vital signals; values is a pair( (x,y), [<vital signals list>] )

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
    
    def aptidao_rn(self, permutacao):
        prioridades = {}

        for idx in range(len(permutacao)):
            id_vitima = permutacao[idx][0]
            x2 = permutacao[idx][2]

            pos_vitima = permutacao[idx][1]  #posicao da vitima
            x3 = self.tempo_deslocamento((0,0),pos_vitima)
            
            x1 = self.dificuldade(pos_vitima)

            x4 = self.aptidao(permutacao)

            x = [x1,x2,x3,x4]
            fitness = fitnessRN(x)
            prioridades[id_vitima] = fitness.make_prediction()

        # Ordenar os itens do dicionário original com base nos valores
        sorted_items = sorted(prioridades.items(), key=lambda item: item[1],reverse=True)

        # Criar um novo dicionário com valores a partir de 0
        ordem_salvamento_prioridades = {item[0]: index for index, item in enumerate(sorted_items)}
        error = 0
        for idx in permutacao:
            id_vitima = idx[0]
            for ix in permutacao:
                if ix[0] == id_vitima:
                        ordem_permutacao = permutacao.index(ix)
                        break
            ordem_prioridade = ordem_salvamento_prioridades[id_vitima]
            error += abs(ordem_permutacao - ordem_prioridade)

        score = 0
        if error == 0:
            score = 100
        else:
            score = 1/error
        return score
             
    def dificuldade(self, pos):
        dificuldade = 0
        self.incr = {              # the increments for each walk action
            0: (0, -1),             #  u: Up
            1: (1, -1),             # ur: Upper right diagonal
            2: (1, 0),              #  r: Right
            3: (1, 1),              # dr: Down right diagonal
            4: (0, 1),              #  d: Down
            5: (-1, 1),             # dl: Down left left diagonal
            6: (-1, 0),             #  l: Left
            7: (-1, -1)             # ul: Up left diagonal
        }

        for direcao in self.incr.values():
            walk = (0,0)
            walk = (pos[0] + direcao[0],pos[1] + direcao[1])
            dificuldade += self.map.get_difficulty(walk)
        return dificuldade

    # Considera só a gravidade e nao as distancias

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
        elif iteracoes_geneticas >= 2:
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
            pontuacao_rota_atual = self.aptidao_rn(permutation)
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

    def sequencing(self, i):
        """ Currently, this method sort the victims by the x coordinate followed by the y coordinate
            @TODO It must be replaced by a Genetic Algorithm that finds the possibly best visiting order """

        """ We consider an agent may have different sequences of rescue. The idea is the rescuer can execute
            sequence[0], sequence[1], ...
            A sequence is a dictionary with the following structure: [vic_id]: ((x,y), [<vs>]"""

        print("🤖 Inicio do sequenciamento:")
        print()
        #victims_info_array = [[1, (4, 2), 0], [2, (0, 0), 1], [3, (1, 5), 2],  [
           #4, (3, 3), 3], [5, (4, 2), 3], [6, (4, 2), 2], [7, (4, 2), 1]]
        
        #if i > 1:
         #   victims_info_array = self.clusters
        #else:
        victims_info_array = self.clusters[i]
        my_sequences = self.sequencia(victims_info_array, [], [], [], 0)
        self.sequences = dict(my_sequences)
        #self.sequences = self.sequencia(self.victims_to_be_saved, [], [], [], 0)
        print("🤖 Fim do sequenciamento, rota de salvamento:")
        print(self.sequences)
        print()
        # Salva a sequencia de salvamento desse agente num .txt
        self.save_sequence_csv(i, my_sequences)

    def planner(self):
        """ A method that calculates the path between victims: walk actions in a OFF-LINE MANNER (the agent plans, stores the plan, and
            after it executes. Eeach element of the plan is a pair dx, dy that defines the increments for the the x-axis and  y-axis."""


        # let's instantiate the breadth-first search
        bfs = BFS(self.map, self.COST_LINE, self.COST_DIAG)

        # for each victim of the first sequence of rescue for this agent, we're going go calculate a path
        # starting at the base - always at (0,0) in relative coords
        
        if not self.sequences:   # no sequence assigned to the agent, nothing to do
            return

        # we consider only the first sequence (the simpler case)
        # The victims are sorted by x followed by y positions: [vic_id]: ((x,y), [<vs>]

        sequence = self.sequences[0]
        start = (0,0) # always from starting at the base
        for vic_id in sequence:
            goal = sequence[vic_id][0]
            plan, time = bfs.search(start, goal, self.plan_rtime)
            self.plan = self.plan + plan
            self.plan_rtime = self.plan_rtime - time
            start = goal

        # Plan to come back to the base
        goal = (0,0)
        plan, time = bfs.search(start, goal, self.plan_rtime)
        self.plan = self.plan + plan
        self.plan_rtime = self.plan_rtime - time
           

    def sync_explorers(self, explorer_map, victims):
        """ This method should be invoked only to the master agent

        Each explorer sends the map containing the obstacles and
        victims' location. The master rescuer updates its map with the
        received one. It does the same for the victims' vital signals.
        After, it should classify each severity of each victim (critical, ..., stable);
        Following, using some clustering method, it should group the victims and
        and pass one (or more)clusters to each rescuer """

        self.received_maps += 1

        print(f"{self.NAME} Map received from the explorer")
        self.map.update(explorer_map)
        self.victims.update(victims)

        if self.received_maps == self.nb_of_explorers:
            print(f"{self.NAME} all maps received from the explorers")
            #self.map.draw()
            #print(f"{self.NAME} found victims by all explorers:\n{self.victims}")

            #predict the severity and the class of victims' using a classifier
            self.predict_severity_and_class()

            cluster = Cluster()
            victims, dfs = cluster.cluster_with_victim_class(self.victims, method='kmeans')
            victim_clusters = victims

            for i in range(4):
                self.save_cluster_csv(dfs[i], i+1)    # file names start at 1 
  
            # Instantiate the other rescuers
            rescuers = [None] * 4
            rescuers[0] = self                    # the master rescuer is the index 0 agent

            # Assign the cluster the master agent is in charge of 
            self.clusters = victim_clusters  # the first one

            #Instantiate the other rescuers and assign the clusters to them
            for i in range(1, 3):    
                #print(f"{self.NAME} instantianting rescuer {i+1}, {self.get_env()}")
                filename = f"rescuer_{i+1:1d}_config.txt"
                config_file = os.path.join(self.config_folder, filename)
                # each rescuer receives one cluster of victims
                rescuers[i] = Rescuer(self.env, config_file, self.config_folder, 1, self.clusters[i+1]) 
                rescuers[i].map = self.map     # each rescuer have the map
                
            # Calculate the sequence of rescue for each agent
            # In this case, each agent has just one cluster and one sequence
            self.sequences = self.clusters         

            # For each rescuer, we calculate the rescue sequence 
            for i, rescuer in enumerate(rescuers):
                self.sequencing(i+1)         # the sequencing will reorder the cluster            
                self.planner()            # make the plan for the trajectory
                self.set_state(VS.ACTIVE) # from now, the simulator calls the deliberation method 
    
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
        
    def deliberate(self) -> bool:
        """ This is the choice of the next action. The simulator calls this
        method at each reasonning cycle if the agent is ACTIVE.
        Must be implemented in every agent
        @return True: there's one or more actions to do
        @return False: there's no more action to do """

        # No more actions to do
        if self.plan == []:  # empty list, no more actions to do
           print(f"{self.NAME} has finished the plan [ENTER]")
           return False

        # Takes the first action of the plan (walk action) and removes it from the plan
        dx, dy = self.plan.pop(0)
        #print(f"{self.NAME} pop dx: {dx} dy: {dy} ")

        # Walk - just one step per deliberation
        walked = self.walk(dx, dy)

        # Rescue the victim at the current position
        if walked == VS.EXECUTED:
            self.x += dx
            self.y += dy
            #print(f"{self.NAME} Walk ok - Rescuer at position ({self.x}, {self.y})")

            # check if there is a victim at the current position
            if self.map.in_map((self.x, self.y)):
                vic_id = self.map.get_vic_id((self.x, self.y))
                if vic_id != VS.NO_VICTIM:
                    self.first_aid()
                    #if self.first_aid(): # True when rescued
                        #print(f"{self.NAME} Victim rescued at ({self.x}, {self.y})")                    
        else:
            print(f"{self.NAME} Plan fail - walk error - agent at ({self.x}, {self.x})")
            
        return True

# # Classe que define o Agente Rescuer com um plano fixo
# class Rescuer(AbstAgent):
#     def __init__(self, env, config_file, nb_of_explorers=1,clusters=[]):
#         """ 
#         @param env: a reference to an instance of the environment class
#         @param config_file: the absolute path to the agent's config file"""

#         super().__init__(env, config_file)

#         # Specific initialization for the rescuer
#         self.map = None             # explorer will pass the map
#         self.victims = None         # list of found victims
#         self.plan = []              # a list of planned actions
#         self.plan_x = 0             # the x position of the rescuer during the planning phase
#         self.plan_y = 0             # the y position of the rescuer during the planning phase
#         self.plan_visited = set()   # positions already planned to be visited
#         self.plan_rtime = self.TLIM  # the remaing time during the planning phase
#         self.plan_walk_time = 0.0   # previewed time to walk during rescue
#         self.x = 0                  # the current x position of the rescuer when executing the plan
#         self.y = 0                  # the current y position of the rescuer when executing the plan

#         self.clusters = clusters     # the clusters of victims this agent should take care of - see the method cluster_victims
#         self.sequences = clusters    # the sequence of visit of victims for each cluster 
        
#         # Starts in IDLE state.
#         # It changes to ACTIVE when the map arrives
#         self.set_state(VS.IDLE)

        
#     def go_save_victims(self, map, victims):
#         """ The explorer sends the map containing the walls and
#         victims' location. The rescuer becomes ACTIVE. From now,
#         the deliberate method is called by the environment"""

#         print(f"\n\n*** R E S C U E R ***")
#         self.map = map
#         print(f"{self.NAME} Map received from the explorer")
#         self.map.draw()

#         # print(f"{self.NAME} List of found victims received from the explorer")
#         self.victims = victims

#         # print the found victims - you may comment out
#         # for seq, data in self.victims.items():
#         #    coord, vital_signals = data
#         #    x, y = coord
#         #    print(f"{self.NAME} Victim seq number: {seq} at ({x}, {y}) vs: {vital_signals}")

#         # print(f"{self.NAME} time limit to rescue {self.plan_rtime}")

#         self.__planner()
#         print(f"{self.NAME} PLAN")
#         i = 1
#         self.plan_x = 0
#         self.plan_y = 0
#         for a in self.plan:
#             self.plan_x += a[0]
#             self.plan_y += a[1]
#             print(
#                 f"{self.NAME} {i}) dxy=({a[0]}, {a[1]}) vic: a[2] => at({self.plan_x}, {self.plan_y})")
#             i += 1

#         print(f"{self.NAME} END OF PLAN")

#         self.set_state(VS.ACTIVE)

#         print("🤖 Inicio do sequenciamento:")
#         print()
#         victims_info_array = [[1, (4, 2), 0], [2, (0, 0), 1], [3, (1, 5), 2],  [
#            4, (3, 3), 3], [5, (4, 2), 3], [6, (4, 2), 2], [7, (4, 2), 1]]
#         self.sequences = self.sequencia(victims_info_array, [], [], [], 0)
#         #self.sequences = self.sequencia(self.victims_to_be_saved, [], [], [], 0)
#         print("🤖 Fim do sequenciamento, rota de salvamento:")
#         print(self.sequences)
#         print()
#         # Salva a sequencia de salvamento desse agente num .txt
#         self.save_sequence_csv(self.id, self.sequences)

#     # num: o numero do rescuer, de 1 a 4
#     # sequence: a sequencia de salvamento das vitimas, um array de arrays
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
    
    def walk_with_astar(self, start, goal):
        # monta grafo com as posicoes exploradas (o mapa) usando matriz de adjacencias
        adjacency_matrix = self.build_adjacency_matrix()

        # Uso do A* para achar o caminho mais curto de volta
        shortest_path = self.find_shortest_path(adjacency_matrix, start, goal)
        
        # Verificar se o caminho foi encontrado
        if len(shortest_path) >= 2:
            # O próximo movimento será a próxima posição no caminho mais curto
            next_position = shortest_path[0]  # A primeira posição é a atual
            dx = next_position[0] + self.x
            dy = next_position[1] + self.y

            # Executar o movimento
            result = self.walk(dx, dy)

            # Verificar se o movimento foi bem-sucedido
            if result == VS.EXECUTED:
                # Atualizar a posição do agente
                self.x = shortest_path[1][0]
                self.y = shortest_path[1][1]
                return True
            elif result == VS.BUMPED:
                print(f"{self.NAME}: when coming back bumped at ({self.x+dx}, {self.y+dy}) , rtime: {self.get_rtime()}")
                return False
        else:
            # Se o caminho não foi encontrado, não há ação a ser tomada
            print("Caminho não encontrado.")
            return False
    # def __depth_search(self, actions_res):
    #     enough_time = True
    #     # print(f"\n{self.NAME} actions results: {actions_res}")
    #     for i, ar in enumerate(actions_res):

    #         if ar != VS.CLEAR:
    #             # print(f"{self.NAME} {i} not clear")
    #             continue

    #         # planning the walk
    #         # get the increments for the possible action
    #         dx, dy = Rescuer.AC_INCR[i]
    #         target_xy = (self.plan_x + dx, self.plan_y + dy)

    #         # checks if the explorer has not visited the target position
    #         if not self.map.in_map(target_xy):
    #             # print(f"{self.NAME} target position not explored: {target_xy}")
    #             continue

    #         # checks if the target position is already planned to be visited
    #         if (target_xy in self.plan_visited):
    #             # print(f"{self.NAME} target position already visited: {target_xy}")
    #             continue

    #         # Now, the rescuer can plan to walk to the target position
    #         self.plan_x += dx
    #         self.plan_y += dy
    #         difficulty, vic_seq, next_actions_res = self.map.get(
    #             (self.plan_x, self.plan_y))
    #         # print(f"{self.NAME}: planning to go to ({self.plan_x}, {self.plan_y})")

    #         if dx == 0 or dy == 0:
    #             step_cost = self.COST_LINE * difficulty
    #         else:
    #             step_cost = self.COST_DIAG * difficulty

    #         # print(f"{self.NAME}: difficulty {difficulty}, step cost {step_cost}")
    #         # print(f"{self.NAME}: accumulated walk time {self.plan_walk_time}, rtime {self.plan_rtime}")

    #         # check if there is enough remaining time to walk back to the base
    #         if self.plan_walk_time + step_cost > self.plan_rtime:
    #             enough_time = False
    #             # print(f"{self.NAME}: no enough time to go to ({self.plan_x}, {self.plan_y})")

    #         if enough_time:
    #             # the rescuer has time to go to the next position: update walk time and remaining time
    #             self.plan_walk_time += step_cost
    #             self.plan_rtime -= step_cost
    #             self.plan_visited.add((self.plan_x, self.plan_y))

    #             if vic_seq == VS.NO_VICTIM:
    #                 self.plan.append((dx, dy, False))  # walk only
    #                 # print(f"{self.NAME}: added to the plan, walk to ({self.plan_x}, {self.plan_y}, False)")

    #             if vic_seq != VS.NO_VICTIM:
    #                 # checks if there is enough remaining time to rescue the victim and come back to the base
    #                 if self.plan_rtime - self.COST_FIRST_AID < self.plan_walk_time:
    #                     print(f"{self.NAME}: no enough time to rescue the victim")
    #                     enough_time = False
    #                 else:
    #                     self.plan.append((dx, dy, True))
    #                     # print(f"{self.NAME}:added to the plan, walk to and rescue victim({self.plan_x}, {self.plan_y}, True)")
    #                     self.plan_rtime -= self.COST_FIRST_AID

    #         # let's see what the agent can do in the next position
    #         if enough_time:
    #             self.__depth_search(self.map.get((self.plan_x, self.plan_y))[
    #                                 2])  # actions results
    #         else:
    #             return

    #     return

    # def __planner(self):
    #     """ A private method that calculates the walk actions in a OFF-LINE MANNER to rescue the
    #     victims. Further actions may be necessary and should be added in the
    #     deliberata method"""

    #     """ This plan starts at origin (0,0) and chooses the first of the possible actions in a clockwise manner starting at 12h.
    #     Then, if the next position was visited by the explorer, the rescuer goes to there. Otherwise, it picks the following possible action.
    #     For each planned action, the agent calculates the time will be consumed. When time to come back to the base arrives,
    #     it reverses the plan."""

    #     # This is a off-line trajectory plan, each element of the list is a pair dx, dy that do the agent walk in the x-axis and/or y-axis.
    #     # Besides, it has a flag indicating that a first-aid kit must be delivered when the move is completed.
    #     # For instance (0,1,True) means the agent walk to (x+0,y+1) and after walking, it leaves the kit.

    #     # always start from the base, so it is already visited
    #     self.plan_visited.add((0, 0))
    #     difficulty, vic_seq, actions_res = self.map.get((0, 0))
    #     self.__depth_search(actions_res)

    #     # push actions into the plan to come back to the base
    #     if self.plan == []:
    #         return

    #     come_back_plan = []

    #     for a in reversed(self.plan):
    #         # triple: dx, dy, no victim - when coming back do not rescue any victim
    #         come_back_plan.append((a[0]*-1, a[1]*-1, False))

    #     self.plan = self.plan + come_back_plan

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
    # def populacao_inicial(self, victims_info_inicial):
    #     lista_1 = random.sample(victims_info_inicial,
    #                             len(victims_info_inicial))
    #     lista_2 = random.sample(victims_info_inicial,
    #                             len(victims_info_inicial))
    #     lista_3 = random.sample(victims_info_inicial,
    #                             len(victims_info_inicial))
    #     lista_4 = random.sample(victims_info_inicial,
    #                             len(victims_info_inicial))

    #     return lista_1, lista_2, lista_3, lista_4

    # # Funcao auxiliar: Calcula a gravidade ponderada de uma rota:
    # # Para todos os itens: multiplica o inverso da posicao no array, pela gravidade dessa posicao
    # # Assim, arrays que tiverem ordenados de maior a menor gravidade, terão uma gravidade ponderada (score) maior
    # # rota: recebe um array de arrays, onde:
    # #  o primeiro item é o id da vitima
    # #  o segundo item é a posicao da vitima
    # #  o terceiro item é a gravidade da vitima
    # def calcular_gravidades_ponderadas(self, rota):
    #     gravidades_ponderadas = []
    #     for idx, info in enumerate(rota):
    #         gravidade = info[2]
    #         gravidade_ponderada = (1 / (idx + 1)) * gravidade
    #         gravidades_ponderadas.append(gravidade_ponderada)
    #     return gravidades_ponderadas

    # # Funcao auxiliar: calcula o tempo de deslocamento entre dois pontos no mapa
    # def tempo_deslocamento(self, pos1, pos2):
    #     # Uso do A* para determinar a distancia entre dois pontos
    #     adjacency_matrix = self.build_adjacency_matrix()
    #     shortest_path = self.find_shortest_path(adjacency_matrix, pos1, pos2)
    #     tamanho = len(shortest_path)

    #     return tamanho

    # def find_shortest_path(self, graph, start, goal):
    #     astar = AStarExplorer(graph, start, goal,
    #                           self.COST_DIAG, self.COST_LINE, self.map)
    #     path = list(astar.find_path())
    #     return path

    # # Retorna um objeto adjacency_matrix[i][j], que vale 1 se há uma aresta entre os vértices i e j, e 0 caso contrário.
    # # Cada vértice na matriz corresponde a uma posição visitada pelo agente no mapa.
    # def build_adjacency_matrix(self):
    #     adjacency_matrix = [[0] * len(self.map.map_data)
    #                         for _ in range(len(self.map.map_data))]

    #     # Mapeia as coordenadas visitadas para seus índices na matriz
    #     coord_to_index = {}
    #     index = 0
    #     for coord in self.map.map_data.keys():
    #         coord_to_index[coord] = index
    #         index += 1

    #     # Preenche a matriz de adjacências
    #     for coord, data in self.map.map_data.items():
    #         x, y = coord
    #         for dx in [-1, 0, 1]:
    #             for dy in [-1, 0, 1]:
    #                 if dx == 0 and dy == 0:
    #                     continue  # Ignora a própria posição
    #                 neighbor_coord = (x + dx, y + dy)
    #                 if self.map.in_map(neighbor_coord):
    #                     # Se a vizinhança foi visitada, atualize a matriz de adjacências
    #                     if data[0] != VS.WALL and self.map.map_data[neighbor_coord][0] != VS.WALL:
    #                         adjacency_matrix[coord_to_index[coord]
    #                                          ][coord_to_index[neighbor_coord]] = 1

    #     return adjacency_matrix

    # # Função de aptidão
    # # Avalia quão boa é uma solução, gerada com o caixeiro viajante, tendo como entrada uma possivel rota
    # # permutacao: recebe um array de arrays, onde
    # #  o primeiro item é o id da vitima
    # #  o segundo item é a posicao da vitima
    # #  o terceiro item é a gravidade da vitima
    # def aptidao(self, permutacao):
    #     gravidade_ponderada = self.calcular_gravidades_ponderadas(permutacao)
    #     soma_gravidade_ponderada = sum(gravidade_ponderada)

    #     pos_atual = self.x, self.y
    #     distancia_total = 0
    #     for posicoes in permutacao:
    #         proxima_pos = posicoes[1]  # pega posicao da vitima
    #         # tempo para ir da posicao atual ate a proxima vitima
    #         distancia = self.tempo_deslocamento(pos_atual, proxima_pos)
    #         distancia_total += distancia
    #         pos_atual = proxima_pos

    #     # O score deve ser maior quanto maior a gravidade ponderada, e menor a distancia que precisa ser percorrida
    #     return soma_gravidade_ponderada + (1/distancia_total)

    # # Considera só a gravidade e nao as distancias

    # def aptidao_v2(self, permutacao):
    #     gravidade_ponderada = self.calcular_gravidades_ponderadas(permutacao)
    #     soma_gravidade_ponderada = sum(gravidade_ponderada)

    #     # O score deve ser maior quanto maior a gravidade ponderada
    #     return soma_gravidade_ponderada

    # # Mutação:
    # # Aplica operadores de mutação para introduzir diversidade na população. Faz isso trocando duas posicoes de uma rota
    # def mutate(self, route):
    #     # Escolher aleatoriamente dois índices distintos na lista
    #     idx1, idx2 = random.sample(range(len(route)), 2)
    #     # Trocar os elementos nos índices selecionados
    #     route[idx1], route[idx2] = route[idx2], route[idx1]
    #     return route

    # # Recombinação (Crossover):
    # # Aplica operadores de crossover (recombinação) para criar novos indivíduos (soluções).
    # def crossover(self, route1, route2):
    #     # Escolher um ponto de corte aleatório
    #     crossover_point = random.randint(1, len(route1) - 1)
    #     # Trocar as subsequências das rotas a partir do ponto de corte
    #     new_route1 = route1[:crossover_point] + \
    #         [pos for pos in route2 if pos not in route1[:crossover_point]]
    #     new_route2 = route2[:crossover_point] + \
    #         [pos for pos in route1 if pos not in route2[:crossover_point]]

    #     return new_route1, new_route2

    # # Funcao auxiliar: usada para retornar uma lista de prioridades de posicoes, para uma lista de posicoes
    # # exemplo:
    # # list = [(0, 0), (1,2), (3,0), (6, 7)]
    # # permutation = [0, 3, 1, 2]
    # # return = [(0,0), (6,7),(1,2),(3,0)]
    # def convert_to_position(self, positions, permutation):
    #     return [positions[i] for i in permutation]

    # # Funçoes aulixiares do algoritmo escolhido: Caixeiro viajante
    # # gera a matriz de distancias
    # def calculate_distance(self, pos1, pos2):
    #     x1, y1 = pos1
    #     x2, y2 = pos2
    #     return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    # def generate_distance_matrix(self, victims_info):
    #     positions = [info[1] for info in victims_info]
    #     n = len(positions)
    #     distance_matrix = [[0] * n for _ in range(n)]
    #     for i in range(n):
    #         for j in range(n):
    #             distance_matrix[i][j] = self.calculate_distance(
    #                 positions[i], positions[j])
    #     return distance_matrix

    # # melhor_lista: parametro obrigatorio
    # # na primeira chamada da funcao deve ser o grupo inicial de vitimas
    # # nas demais, a propria funcao irá se chamar com a melhor lista ate entao
    # def sequencia(self, melhor_lista, segunda_lista, terceira_lista, quarta_lista, iteracoes_geneticas):
    #     if iteracoes_geneticas == 0:
    #         # Passo 1: Populacao inicial
    #         lista_1, lista_2, lista_3, lista_4 = self.populacao_inicial(
    #             melhor_lista)
    #     elif iteracoes_geneticas >= 20:
    #         # TODO: Colocar numero do criterio de parada numa variavel separada
    #         # Passo final: criterio de parada
    #         return melhor_lista
    #     else:
    #         # já iterei alguma vez e já possuo 4 individuos na populacao
    #         lista_1, lista_2, lista_3, lista_4 = melhor_lista, segunda_lista, terceira_lista, quarta_lista

    #     print("primeira selecao")
    #     # Passo 2: Seleção
    #     # Seleciona 2 melhores indivíduos da população atual para reprodução
    #     all_lists = [lista_1, lista_2, lista_3, lista_4]
    #     melhor_pontuacao = 1
    #     melhor_rota = lista_1
    #     segunda_melhor_pontuacao = 0
    #     segunda_melhor_rota = lista_2

    #     for i, lista in enumerate(all_lists):
    #         distance_matrix = self.generate_distance_matrix(lista)
    #         distance_matrix = np.array(distance_matrix)
    #         permutation, distance = solve_tsp_dynamic_programming(
    #             distance_matrix)

    #         print("🧾 {}ª lista sendo avaliada para selecao:".format(i+1))
    #         permutation = self.convert_to_position(lista, permutation)
    #         print("Lista: {}".format(permutation))

    #         # Passo 3: Usar a funcao de aptidao para cumprir o passo 2
    #         pontuacao_rota_atual = self.aptidao(permutation)
    #         print("Pontuacao:", pontuacao_rota_atual)
    #         if pontuacao_rota_atual > melhor_pontuacao:
    #             melhor_pontuacao = pontuacao_rota_atual
    #             melhor_rota = permutation
    #             melhor_distancia = distance
    #         else:
    #             if pontuacao_rota_atual > segunda_melhor_pontuacao:
    #                 segunda_melhor_pontuacao = pontuacao_rota_atual
    #                 segunda_melhor_rota = permutation
    #                 segunda_melhor_distancia = distance

    #     print("🌳 Melhores rotas (individuos) pós seleção:")
    #     print("Pai 1:", melhor_rota)
    #     print("Pai 2:", segunda_melhor_rota)

    #     # Passo 4: Recombinação (Crossover):
    #     # Vamos usar os dois melhores individuos, gerados na ultima etapa, para criar mais dois
    #     nova_rota1, nova_rota2 = self.crossover(
    #         melhor_rota, segunda_melhor_rota)
    #     print("🍓 Dois novos individuos pós crossover:")
    #     print("Nova Rota 1:", nova_rota1)
    #     print("Nova Rota 2:", nova_rota2)

    #     # Passo 5: Mutação:
    #     # Gera uma mutação aleatória em um dos indivíduos da população
    #     nova_rota1 = self.mutate(nova_rota1)
    #     print("Inidividuo nova_rota_1 mutado, pós mutação:", nova_rota1)

    #     print("Fim da {} iteracao".format(iteracoes_geneticas+1))
    #     print()

    #     iteracoes_geneticas += 1
    #     # Loop até que seja atingido o critério de parada
    #     return self.sequencia(melhor_rota, segunda_melhor_rota, nova_rota1, nova_rota2, iteracoes_geneticas)

# *********************************
#  Deliberate

    # def deliberate(self) -> bool:
    #     """ This is the choice of the next action. The simulator calls this
    #     method at each reasonning cycle if the agent is ACTIVE.
    #     Must be implemented in every agent
    #     @return True: there's one or more actions to do
    #     @return False: there's no more action to do """

    #     # No more actions to do
    #     if self.plan == []:  # empty list, no more actions to do
    #         # input(f"{self.NAME} has finished the plan [ENTER]")
    #         return False

    #     # Takes the first action of the plan (walk action) and removes it from the plan
    #     dx, dy, there_is_vict = self.plan.pop(0)
    #     # print(f"{self.NAME} pop dx: {dx} dy: {dy} vict: {there_is_vict}")

    #     # Walk - just one step per deliberation
    #     walked = self.walk(dx, dy)

    #     # Rescue the victim at the current position
    #     if walked == VS.EXECUTED:
    #         self.x += dx
    #         self.y += dy
    #         # print(f"{self.NAME} Walk ok - Rescuer at position ({self.x}, {self.y})")
    #         # check if there is a victim at the current position
    #         if there_is_vict:
    #             rescued = self.first_aid()  # True when rescued
    #             if rescued:
    #                 print(f"{self.NAME} Victim rescued at ({self.x}, {self.y})")
    #             else:
    #                 print(
    #                     f"{self.NAME} Plan fail - victim not found at ({self.x}, {self.x})")
    #     else:
    #         print(
    #             f"{self.NAME} Plan fail - walk error - agent at ({self.x}, {self.x})")

    #     # input(f"{self.NAME} remaining time: {self.get_rtime()} Tecle enter")

    #     return True
