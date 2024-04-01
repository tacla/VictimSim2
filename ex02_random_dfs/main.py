import sys
import os
import time

## importa classes
from vs.environment import Env
from explorer import Explorer
from rescuer import Rescuer
from cluster import Cluster

def main(data_folder_name):
   
    # Set the path to config files and data files for the environment
    current_folder = os.path.abspath(os.getcwd())
    data_folder = os.path.abspath(os.path.join(current_folder, data_folder_name))

    
    # Instantiate the environment
    env = Env(data_folder)
    
    # config files for the agents
    rescuer_file = os.path.join(data_folder, "rescuer_config.txt")
    explorer_file = os.path.join(data_folder, "explorer_config.txt")
    
    # Instantiate agents rescuer and explorer
    resc = Rescuer(env, rescuer_file)

    # Explorer needs to know rescuer to send the map
    # that's why rescuer is instatiated before
    exp_1 = Explorer(env, explorer_file, resc)
    exp_2 = Explorer(env, explorer_file, resc)
    exp_3 = Explorer(env, explorer_file, resc)
    exp_4 = Explorer(env, explorer_file, resc)

    # Run the environment simulator
    env.run()

    # Clustering
    cluster = Cluster()
    exp_victims = {} # dictionary that will agregate all found victims

    for explorer in [exp_1, exp_2, exp_3, exp_4]:
        if explorer.victims != {}:
            if exp_victims == {}:
                exp_victims = explorer.victims
            else:
                exp_victims.update(explorer.victims)

    cluster_victims = cluster.cluster(exp_victims)
    
        
if __name__ == '__main__':
    """ To get data from a different folder than the default called data
    pass it by the argument line"""
    
    if len(sys.argv) > 1:
        data_folder_name = sys.argv[1]
    else:
        data_folder_name = os.path.join("datasets", "data_42v_20x20")
        
    main(data_folder_name)
