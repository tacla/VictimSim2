import sys
import os

from vs.environment import Env
from explorer import Explorer
from rescuer import Rescuer
from pathlib import Path

def main(data_folder, agent_config_folder):
    """To get data from a different folder than the default called data
    pass it by the argument line"""

    # instanciando o ambiente
    environment = Env(data_folder)
    
    # carregando os arquivos de configuração dos agentes
    rescuer_file = os.path.join(agent_config_folder, "rescuer_1_config.txt")
    explorer_file = os.path.join(agent_config_folder, "explorer_1_config.txt")
    
    print(rescuer_file)
    # Instanciando os agentes socorrista e explorador
    # O explorador precisa conhecer o socorrista para enviar o mapa, por isso o socorrista deve ser inicializado antes
    rescuer = Rescuer(environment, rescuer_file)
    explorer = Explorer(environment, explorer_file, rescuer)

    # Executa o simulador do ambiente
    environment.run()


if __name__ == '__main__':
    
    current_folder = Path.cwd()

    if len(sys.argv) > 1:
        data_folder = sys.argv[1]
    else:
        data_folder = os.path.join(current_folder.parent, "datasets", "data_10v_12x12")
        
    if len(sys.argv) > 2:
        agent_config_folder = sys.argv[2]
    else:
        agent_config_folder = os.path.join(current_folder, "config")

    main(data_folder, agent_config_folder)
