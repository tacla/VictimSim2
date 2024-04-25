import sys
import os
import time
import pandas as pd
from joblib import load

# importa classes
from vs.environment import Env
from explorer import Explorer
from rescuer import Rescuer
from cluster import Cluster
from map import Map


def main(data_folder_name):

    # Set the path to config files and data files for the environment
    current_folder = os.path.abspath(os.getcwd())
    data_folder = os.path.abspath(
        os.path.join(current_folder, data_folder_name))

    # Instantiate the environment
    env = Env(data_folder)

    # config files for the agents
    rescuer_file = os.path.join(data_folder, "rescuer_config.txt")
    explorer_file = os.path.join(data_folder, "explorer_config.txt")

    # Instantiate agents rescuer and explorer
    resc = Rescuer(env, rescuer_file)

    # Explorer needs to know rescuer to send the map
    # that's why rescuer is instatiated before
    exp = Explorer(env, explorer_file, resc)
    exp2 = Explorer(env, explorer_file, resc)
    exp3 = Explorer(env, explorer_file, resc)
    exp4 = Explorer(env, explorer_file, resc)

    # Run the environment simulator
    env.run()

    # Join all maps
    complete_map = Map()
    complete_map.map_data = exp.map.map_data | exp2.map.map_data | exp3.map.map_data | exp4.map.map_data

    # Condensate all victims data
    total_victims = {}
    for ex in [exp, exp2, exp3, exp4]:
        if ex.victims != {}:
            if total_victims == {}:
                total_victims = ex.victims
            else:
                total_victims.update(ex.victims)
    
    # Classification
    df_victims = pd.DataFrame()
    ids = []
    qpa = []
    pulso = []
    resp = []
    for v in total_victims.values():
        ids.append(v[1][0])
        qpa.append(v[1][3])
        pulso.append(v[1][4])
        resp.append(v[1][5])
    df_victims['id'] = pd.Series(ids)
    df_victims['qpa'] = pd.Series(qpa)
    df_victims['pulso'] = pd.Series(pulso)
    df_victims['resp'] = pd.Series(resp)

    tree_model = load('decision_tree_model.joblib')
    X = df_victims
    y_pred = tree_model.predict(X)
    print(y_pred)
    # cluster = Cluster()
    # victims_with_cluster = cluster.cluster(total_victims)


if __name__ == '__main__':
    """ To get data from a different folder than the default called data
    pass it by the argument line"""

    if len(sys.argv) > 1:
        data_folder_name = sys.argv[1]
    else:
        data_folder_name = os.path.join("datasets", "data_10v_12x12")

    main(data_folder_name)
