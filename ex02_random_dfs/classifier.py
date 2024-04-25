import pandas as pd
from joblib import load
import os

class Classifier():
    def __init__(self,total_victims):
        self.total_victims = total_victims
        self.create_dataframe()

    def create_dataframe(self):
        self.df_victims = pd.DataFrame()
        ids = []
        qpa = []
        pulso = []
        resp = []
        for v in self.total_victims.values():
            ids.append(v[1][0])
            qpa.append(v[1][3])
            pulso.append(v[1][4])
            resp.append(v[1][5])
        self.df_victims['Id'] = pd.Series(ids)
        self.df_victims['qPA'] = pd.Series(qpa)
        self.df_victims['pulso'] = pd.Series(pulso)
        self.df_victims['resp'] = pd.Series(resp)
    
    def make_prediction(self):
        tree_model = load(os.getcwd() + '\\ex02_random_dfs\\decision_tree_model.joblib')
        X = self.df_victims
        y_pred = tree_model.predict(X)
        i = 0
        for v in self.total_victims.values():
            v[1].append(y_pred[i])
            i += 1
        total_victims_with_label = self.total_victims
        return total_victims_with_label