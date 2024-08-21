import tensorflow as tf
from tensorflow.keras import layers, models
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.optimizers import Adam

df = pd.read_csv('env_vital_signals.csv')
# df = pd.read_csv('normalized_env_vital_signals.csv')

X = df[['qPA', 'pulso', 'fResp']]
# y = df['grav']
y = df['label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

y_train -= 1
y_test -= 1

model = models.Sequential([
    layers.Dense(16, activation='relu', input_shape=(X_train.shape[1],)),
    layers.Dense(8, activation='relu'),
    layers.Dense(4, activation='softmax')
])

model.compile(optimizer=Adam(learning_rate=0.0005),
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

model.fit(X_train, y_train, epochs=250, batch_size=64, verbose=1)

test_loss, test_acc = model.evaluate(X_test, y_test, verbose=1)

predictions = model.predict(X_test)

predicted_labels = np.argmax(predictions, axis=1)

predicted_labels += 1

print(predicted_labels)
print(f'Test accuracy: {test_acc}')