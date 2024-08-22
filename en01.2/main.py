import sys
import os
import time

## importa classes
from vs.environment import Env
from explorer import Explorer
from rescuer import Rescuer
from strategy import PRIORITIES
from rescuer_boss import RescuerBoss

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
    resc0 = Rescuer(env, rescuer_file)
    resc1 = Rescuer(env, rescuer_file)
    resc2 = Rescuer(env, rescuer_file)

    resc_b = RescuerBoss(env, rescuer_file, [resc0, resc1, resc2])

    # Explorer needs to know rescuer to send the map
    # that's why rescuer is instatiated before
    exp0 = Explorer(env, explorer_file, resc_b, PRIORITIES[0])
    exp1 = Explorer(env, explorer_file, resc_b, PRIORITIES[1])
    exp2 = Explorer(env, explorer_file, resc_b, PRIORITIES[2])
    exp3 = Explorer(env, explorer_file, resc_b, PRIORITIES[3])

    # Run the environment simulator
    env.run()
    
        
if __name__ == '__main__':
    """ To get data from a different folder than the default called data
    pass it by the argument line"""
    
    if len(sys.argv) > 1:
        data_folder_name = sys.argv[1]
    else:
        # data_folder_name = os.path.join("datasets", "data_10v_12x12")
        # data_folder_name = os.path.join("datasets", "data_42v_20x20")
        # data_folder_name = os.path.join("datasets", "data_132v_100x80")
        # data_folder_name = os.path.join("datasets", "data_225v_100x80")
        data_folder_name = os.path.join("datasets", "data_300v_90x90")
        
    main(data_folder_name)
