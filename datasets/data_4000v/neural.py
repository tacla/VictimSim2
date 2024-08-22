import joblib
import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor
from tensorflow.keras import layers, models
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
    layers.Dense(32, activation='relu', input_shape=(X_train.shape[1],)),
    layers.Dense(16, activation='relu'),
    layers.Dense(1, activation='linear')
])

model.compile(optimizer=Adam(learning_rate=0.0005),
              loss='mean_squared_error',
              metrics=['mean_absolute_error'])

model.fit(X_train, y_train, epochs=500, batch_size=64, verbose=1)

test_loss, test_mae = model.evaluate(X_test, y_test, verbose=1)

predictions = model.predict(X_test)

tree_model = DecisionTreeRegressor(max_depth=50, random_state=42)
tree_model.fit(X_train, y_train)

joblib.dump(tree_model, 'decision_tree_model.pkl')

df = pd.read_csv('../data_800v/normalized_env_vital_signals.csv')

X = df[['qPA', 'pulso', 'fResp']]
y = df['grav']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()

X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

y_pred_nn = model.predict(X_test)
y_pred_tree = tree_model.predict(X_test)

rmse_nn = mean_squared_error(y_test, y_pred_nn, squared=False)
rmse_tree = mean_squared_error(y_test, y_pred_tree, squared=False)

print(f'Test MAE: {test_mae}')
print(f'RMSE NN: {rmse_nn}, RMSE Tree: {rmse_tree}')

model.save('vital_signs_model.h5')