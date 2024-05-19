import pandas as pd
from joblib import load
import os
import pickle

class Regressor():
    def __init__(self,total_victims):
        self.total_victims = total_victims
        self.ids = []
        self.ids = self.create_dataframe()

    def create_dataframe(self):
        self.df_victims = pd.DataFrame()
        qpa = []
        pulso = []
        resp = []
        for v in self.total_victims.values():
            self.ids.append(v[1][0])
            qpa.append(v[1][3])
            pulso.append(v[1][4])
            resp.append(v[1][5])
        
        #self.df_victims['Id'] = pd.Series(ids)
        self.df_victims['qPA'] = pd.Series(qpa)
        self.df_victims['pulso'] = pd.Series(pulso)
        self.df_victims['resp'] = pd.Series(resp)
        return self.ids
    
    def make_prediction(self):
        #tree_model = load(os.getcwd() + '\\ex02_random_dfs\\decision_tree_model.joblib')
        rn_model = pickle.load(open(f"{os.getcwd()}/ex02_random_dfs/model.pkl", "rb"))
        X = self.df_victims
        y_pred = rn_model.predict(X)   
        i = 0
        for id in self.ids:
            v = self.total_victims[id]
            v[1].append(y_pred[i])
            self.total_victims[id] = v
            i += 1
        print('*******', self.total_victims)
        return self.total_victims