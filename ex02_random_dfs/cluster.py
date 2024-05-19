import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, silhouette_samples
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from kneed import KneeLocator
from sklearn.cluster import DBSCAN
import json


class Cluster():

    def __init__(self):
        pass

    def optimal_number_of_clusters_elbow_curve(self, victims):

        y = []
        x = range(1, 11)

        for k in x:
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(victims)
            y.append(kmeans.inertia_)
        
        kn = KneeLocator(
                    x,
                    y,
                    curve='convex',
                    direction='decreasing',
                    interp_method='interp1d',
                ).knee
        
        print(f"Number of rescuers found by elbow-curve analysis:{kn}")
        # plt.plot(x, y, marker='s', color='purple')
        # plt.title('Curva do cotovelo')
        # plt.xlabel('N. de clusters (K)')
        # plt.ylabel('Sum of Squared Error (SSE)')
        # plt.show()

        return kn
    
    def silhouette_analysis(self, victims):
        
        n_samples = len(victims)
        max_clusters = min(10, n_samples - 1)  # Limitando o número máximo de clusters

        for n_clusters in range(2, max_clusters + 1):  # Adicionando 1 ao número máximo de clusters
            kmeans = KMeans(n_clusters=n_clusters, random_state=10)
            cluster_labels = kmeans.fit_predict(victims)
            
            silhouette_avg = silhouette_score(victims, cluster_labels)
            print("For ", n_clusters, "clusters, the average silhouette coef. is :", silhouette_avg)
            
            sample_silhouette_values = silhouette_samples(victims, cluster_labels)
            
            fig, ax = plt.subplots(1, 1)
            ax.set_xlim([-0.1, 1])
            ax.set_ylim([0, len(victims) + (n_clusters + 1) * 10])
            
            y_lower = 10
            
            for i in range(n_clusters):
                ith_cluster_silhouette_values = sample_silhouette_values[cluster_labels == i]
                ith_cluster_silhouette_values.sort()
                
                size_cluster_i = ith_cluster_silhouette_values.shape[0]
                y_upper = y_lower + size_cluster_i
                
                color = plt.cm.tab20(float(i) / n_clusters)
                ax.fill_betweenx(np.arange(y_lower, y_upper), 0, ith_cluster_silhouette_values, facecolor=color, edgecolor=color, alpha=0.7)
                
                ax.text(-0.05, y_lower + 0.5 * size_cluster_i, f"Cluster {i}")
                
                y_lower = y_upper + 10
            
            ax.set_title(f"Silhouette Plot para {n_clusters} Clusters")
            ax.set_xlabel("Coeficiente de Silhueta")
            ax.set_ylabel("Índice de Amostra e Cluster")
            
            ax.axvline(x=silhouette_avg, color="black", linestyle="--")
            
            ax.set_yticks([])
            ax.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])
            
            plt.show()

    def silhouette_for_n_clusters(self, victims, cluster_labels):

        silhouette_avg = silhouette_score(victims, cluster_labels)
        print("For ", len(set(cluster_labels)), "clusters, the average silhouette coef. is :", silhouette_avg)

    def cluster_with_kmeans(self, victims):
        '''
        Method used by Tarefa 1
        '''
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

    def cluster_models(self, method, kn, x_victims):
        
        if method == 'kmeans':
            kmeans = KMeans(n_clusters=kn, random_state=42)
            kmeans.fit(X=x_victims)
            labels = kmeans.labels_
        elif method == 'hierarquical':
            hierarchical_cluster = AgglomerativeClustering(n_clusters = kn, linkage = "average", metric = "cosine" )
            labels = hierarchical_cluster.fit_predict(x_victims)
        elif method == 'dbscan':
            dbscan_model = DBSCAN(eps=0.25, min_samples=9)
            dbscan_model.fit(x_victims)
            labels = dbscan_model.labels_

        return labels

    def cluster_with_victim_class(self, victims, method, n_rescuers_dynamic=True):
        # TODO: add classification as victim_data[2]

        # Clustering using location,  vital signs and classification
        x_victims = []
        for victim_data in victims.values():
            x_victims.append([victim_data[0][0]] + [victim_data[0][1]] + victim_data[1][-1])
        
        kn = 4
        
        # if number of rescuers can be dynamic, it will find the optimal numbr of clusters through elbow curve analysis
        if n_rescuers_dynamic:
            kn = self.optimal_number_of_clusters_elbow_curve(x_victims)
            print(f"Optimal number of clusters would be:{kn}")
        else:
            print(f"Using static number of rescuers:{kn}")

        # if there are less clusters than rescuers, adapt to 4 clusters
        kn = 4 if kn < 4 else kn

        labels = self.cluster_models(method, kn, x_victims)     

        # Adapt the number of clusters to be equal to number of rescuers  
        if kn > 4:
            labels = self.adapt_clusters_to_4rescuers(x_victims, method='hierarquical')

        i = 0
        for id, victim_data in victims.items():
            victims[id] = (victim_data[0], victim_data[1] + [labels[i]])
            i += 1

        print(f"*** {method} clustering report: ***")

        dfs = []
        for cluster in set(labels):
            c_result = [x[0] for x in victims.values() if x[1][-1] == cluster]
            print(f"Victims to be rescued by rescuer {cluster}: {c_result}")
            df_victims = pd.DataFrame(columns=['id','x','y','grav','classe'])
            df_victims['id'] = pd.Series([value[1][0] for value in victims.values()])
            df_victims['x'] = pd.Series([value[0][0] for value in victims.values()])
            df_victims['y'] = pd.Series([value[0][1] for value in victims.values()])
            df_victims['grav'] = pd.Series(np.zeros(len(victims)))
            df_victims['classe'] = pd.Series([value[1][-2] for value in victims.values()])
            print(df_victims)
            dfs.append(df_victims)
            #with open(f'ex02_random_dfs/cluster{cluster+1}.txt', 'w') as file:
                #file.write(json.dumps(c_result))

        # silhouette analysis to evaluate clustering method
        self.silhouette_for_n_clusters(x_victims, labels)

        victims_cluster_1 = [[x[1][0], x[0], x[1][-1]] for x in victims.values() if x[1][-1] == 0]
        victims_cluster_2 = [[x[1][0], x[0], x[1][-1]] for x in victims.values() if x[1][-1] == 1]
        victims_cluster_3 = [[x[1][0], x[0], x[1][-1]] for x in victims.values() if x[1][-1] == 2]
        victims_cluster_4 = [[x[1][0], x[0], x[1][-1]] for x in victims.values() if x[1][-1] == 3]

        return {1:victims_cluster_1,2:victims_cluster_2,3:victims_cluster_3,4:victims_cluster_4}, dfs


    def adapt_clusters_to_4rescuers(self, x_victims, method=None):

        if method == 'hierarquical':
            # Cut the dendrogram to obtain n clusters == n rescuers
            num_clusters = 4

            Z = linkage(x_victims, method='average', metric='cosine')
            labels = fcluster(Z, num_clusters, criterion='maxclust')
        elif method == 'kmeans':
            desired_num_clusters = 4  # Number of clusters in the end

            clusters_to_merge = num_clusters - desired_num_clusters

            for _ in range(clusters_to_merge):
                # Compute pairwise distances between centroids
                centroid_distances = np.linalg.norm(centroids[:, np.newaxis] - centroids[np.newaxis, :], axis=-1)

                np.fill_diagonal(centroid_distances, np.inf)
                closest_clusters = np.unravel_index(np.argmin(centroid_distances), centroid_distances.shape)

                merged_centroid = np.mean([centroids[closest_clusters[0]], centroids[closest_clusters[1]]], axis=0)
                centroids = np.delete(centroids, closest_clusters[1], axis=0)
                centroids[closest_clusters[0]] = merged_centroid

                labels[labels == closest_clusters[1]] = closest_clusters[0]

        return labels