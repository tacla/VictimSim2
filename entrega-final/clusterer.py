from sklearn.cluster import KMeans

class VictimClusterer:
    def __init__(self, n_clusters=4, random_state=0):
        self.n_clusters = n_clusters
        self.random_state = random_state

    def cluster_victims(self, victims):
        victims_list = []
        keys = []

        for k, v in victims.items():
            x, y = v[0]  # Position of the victim
            sev = v[1][-2]  # Severity score 
            victims_list.append([x, y, sev])
            keys.append(k)

        if not victims_list:
            return []

        kmeans = KMeans(n_clusters=self.n_clusters, random_state=self.random_state)
        kmeans.fit(victims_list)

        labels = kmeans.labels_
        clusters = [{} for _ in range(self.n_clusters)]

        for i, lbl in enumerate(labels):
            clusters[lbl][keys[i]] = victims[keys[i]]

        return clusters
