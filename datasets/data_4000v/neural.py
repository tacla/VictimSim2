import joblib
import tensorflow as tf
from tensorflow.keras import layers, models
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.optimizers import Adam

# df = pd.read_csv('env_vital_signals.csv')
df = pd.read_csv('normalized_env_vital_signals.csv')

X = df[['qPA', 'pulso', 'fResp']]
y = df['grav']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)
joblib.dump(scaler, 'scaler.save')
model = models.Sequential([
    layers.Dense(16, activation='relu', input_shape=(X_train.shape[1],)),
    layers.Dense(8, activation='relu'),
    layers.Dense(1, activation='linear')  # Single neuron for regression
])

model.compile(optimizer=Adam(learning_rate=0.0005),
              loss='mean_squared_error',
              metrics=['mean_absolute_error'])  # Use MAE or RMSE for regression metrics

model.fit(X_train, y_train, epochs=250, batch_size=64, verbose=1)

test_loss, test_mae = model.evaluate(X_test, y_test, verbose=1)

predictions = model.predict(X_test)

print(predictions)  # Directly print or analyze continuous predictions
print(f'Test MAE: {test_mae}')

model.save('vital_signs_model.h5')