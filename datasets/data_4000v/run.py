import tensorflow as tf
import numpy as np
import joblib
import pandas as pd


def predict_grav(qPA, pulso, fResp):
    # Load the model from disk
    model = tf.keras.models.load_model('vital_signs_model.h5')

    # Load the saved scaler
    scaler = joblib.load('scaler.save')

    # Create a DataFrame for the input values
    input_data = pd.DataFrame([[qPA, pulso, fResp]], columns=['qPA', 'pulso', 'fResp'])

    # Scale the input data using the loaded scaler
    input_data_scaled = scaler.transform(input_data)

    # Predict the 'grav' value
    predicted_grav = model.predict(input_data_scaled)

    return predicted_grav[0][0]


# Example usage
qPA = 0.9953601906626027
pulso = 0.6119316720285145
fResp = 0.2555589484697967

predicted_grav = predict_grav(qPA, pulso, fResp)
print(f'Predicted grav: {predicted_grav}')
