import os
import csv
import numpy as np
from sklearn.cluster import KMeans

class Cluster():

    def __init__(self):
        pass

    def cluster(self, victims):
        # Clustering using location and vital signs
        x_victims = []
        for victim_data in victims.values():
            x_victims.append([victim_data[0][0]] + [victim_data[0][1]] + victim_data[1])
        
        
        # we are going to use 4 clusters because we have 4 rescuer agents
        kmeans = KMeans(n_clusters=4, random_state=42)
        kmeans.fit(X=x_victims)
        labels = kmeans.labels_

        i = 0 
        for id, victim_data in victims.items():
            victims[id] = (victim_data[0], victim_data[1] + [labels[i]])
            i += 1

        victims_cluster_1 = [x[0] for x in victims.values() if x[1][-1] == 0]
        victims_cluster_2 = [x[0] for x in victims.values() if x[1][-1] == 1]
        victims_cluster_3 = [x[0] for x in victims.values() if x[1][-1] == 2]
        victims_cluster_4 = [x[0] for x in victims.values() if x[1][-1] == 3]        

        print("*** Clustering report: ***")
        print("Victims to be rescued by rescuer 1: {}".format(victims_cluster_1))
        print("Victims to be rescued by rescuer 2: {}".format(victims_cluster_2))
        print("Victims to be rescued by rescuer 3: {}".format(victims_cluster_3))
        print("Victims to be rescued by rescuer 4: {}".format(victims_cluster_4))

        return victims