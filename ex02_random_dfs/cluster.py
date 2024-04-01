import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, silhouette_samples

class Cluster():

    def __init__(self):
        pass

    def cluster(self, victims):
        # Clustering using location and vital signs
        x_victims = []
        for victim_data in victims.values():
            x_victims.append([victim_data[0][0]] + [victim_data[0][1]] + victim_data[1])
        
        self.number_of_clusters_elbow_curve_analysis(x_victims)
        self.silhouette_analysis(x_victims)
        
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

    def number_of_clusters_elbow_curve_analysis(self, victims):
        sse = []

        # Test different values for K, although we will be using 4 because we have 4 rescuers
        for k in range(1, 11):
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(victims)
            sse.append(kmeans.inertia_)

        plt.plot(range(1, 11), sse, marker='s', color='purple')
        plt.title('Curva do cotovelo')
        plt.xlabel('N. de clusters (K)')
        plt.ylabel('Sum of Squared Error (SSE)')
        plt.show()

    
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
