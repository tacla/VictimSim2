import tensorflow as tf
import numpy as np
import joblib
import pandas as pd


def predict_grav_nn(qPA, pulso, fResp):
    model = tf.keras.models.load_model('vital_signs_model.h5')

    scaler = joblib.load('scaler.save')

    input_data = pd.DataFrame([[qPA, pulso, fResp]], columns=['qPA', 'pulso', 'fResp'])

    input_data_scaled = scaler.transform(input_data)

    predicted_grav = model.predict(input_data_scaled)

    return predicted_grav[0][0]


def predict_grav_tree(qPA, pulso, fResp):
    tree_model = joblib.load('decision_tree_model.pkl')

    scaler = joblib.load('scaler.save')

    input_data = pd.DataFrame([[qPA, pulso, fResp]], columns=['qPA', 'pulso', 'fResp'])

    input_data_scaled = scaler.transform(input_data)

    predicted_grav = tree_model.predict(input_data_scaled)

    return predicted_grav[0]

qPA = 0.18445306489742827
pulso = 0.37382904376219306
fResp = 0.879946156836826
# Expected 0.69419681

predicted_grav = predict_grav_nn(qPA, pulso, fResp)
print(f'Predicted grav NN: {predicted_grav}')

predicted_grav = predict_grav_tree(qPA, pulso, fResp)
print(f'Predicted grav DC: {predicted_grav}')