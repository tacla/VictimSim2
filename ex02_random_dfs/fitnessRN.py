import pandas as pd
from joblib import load
import os
import pickle

class fitnessRN():
    def __init__(self,X):
        self.X = X
    
    def make_prediction(self):
        #tree_model = load(os.getcwd() + '\\ex02_random_dfs\\decision_tree_model.joblib')
        rn_model_ag = pickle.load(open(f"{os.getcwd()}/ex02_random_dfs/model_ag.pkl", "rb"))
        y_pred = rn_model_ag.predict([self.X])
        return y_pred