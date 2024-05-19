import sys
import os

# importa classes
from vs.environment import Env
from explorer import Explorer
from rescuer import Rescuer


def main(data_folder_name):

    # Set the path to config files and data files for the environment
    config_ag_folder = os.path.join("ex02_random_dfs", "cfg_1")
    #config_ag_folder = 'cfg_1'
    current_folder = os.path.abspath(os.getcwd())
    data_folder = os.path.abspath(
        os.path.join(current_folder, data_folder_name))

    # Instantiate the environment
    env = Env(data_folder)

    # config files for the agents
    rescuer_file = os.path.join(config_ag_folder, "rescuer_1_config.txt")
    
    master_rescuer = Rescuer(env, rescuer_file, config_ag_folder, 4)   # 4 is the number of explorer agents

    # Explorer needs to know rescuer to send the map 
    # that's why rescuer is instatiated before
    for exp in range(1, 5):
        filename = f"explorer_{exp:1d}_config.txt"
        explorer_file = os.path.join(config_ag_folder, filename)
        Explorer(env, explorer_file, data_folder, master_rescuer)

    # Run the environment simulator
    env.run() 

if __name__ == '__main__':
    """ To get data from a different folder than the default called data
    pass it by the argument line"""    
    if len(sys.argv) > 1:
        data_folder_name = sys.argv[1]
    else:
        data_folder_name = os.path.join("datasets", "data_42v_20x20")
        
    main(data_folder_name)
