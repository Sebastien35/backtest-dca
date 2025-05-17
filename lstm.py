import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping

# --- Charger les données ---
df = pd.read_csv("daily_close.csv")  # ton fichier BTC daily Close
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date')

# Utiliser uniquement la colonne Close pour le modèle (séries univariées)
close_prices = df['Close'].values.reshape(-1, 1)

# --- Normalisation ---
scaler = MinMaxScaler(feature_range=(0, 1))
close_scaled = scaler.fit_transform(close_prices)

# --- Création des séquences pour LSTM ---
def create_sequences(data, seq_length=60):
    X, y = [], []
    for i in range(len(data) - seq_length - 15):  # 15 jours à prévoir plus tard
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length])
    return np.array(X), np.array(y)

SEQ_LENGTH = 50  # nombre de jours pour prédire le suivant (lookback)
X, y = create_sequences(close_scaled, SEQ_LENGTH)

# Séparer train / test (ex : 80% train)
train_size = int(len(X) * 0.8)
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

# --- Construire le modèle LSTM ---
model = Sequential([
    LSTM(50, return_sequences=True, input_shape=(SEQ_LENGTH, 1)),
    LSTM(50),
    Dense(1)
])

model.compile(optimizer='adam', loss='mse')

# Early stopping pour éviter overfitting
es = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

# --- Entraînement ---
history = model.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=100,
    batch_size=32,
    callbacks=[es],
    verbose=1
)

# --- Prédiction sur test ---
y_pred_scaled = model.predict(X_test)
y_pred = scaler.inverse_transform(y_pred_scaled)
y_test_true = scaler.inverse_transform(y_test)

# --- Évaluation ---
rmse = np.sqrt(mean_squared_error(y_test_true, y_pred))
mae = mean_absolute_error(y_test_true, y_pred)

print(f"📊 Performance du modèle :")
print(f"RMSE = {rmse:.4f}")
print(f"MAE  = {mae:.4f}")

# --- Prédiction sur 15 jours futurs ---
# On part de la dernière séquence connue
last_seq = close_scaled[-SEQ_LENGTH:]  # shape (SEQ_LENGTH, 1)

forecasted = []
current_seq = last_seq.copy()

for _ in range(15):
    pred = model.predict(current_seq.reshape(1, SEQ_LENGTH, 1))[0, 0]
    forecasted.append(pred)
    current_seq = np.append(current_seq[1:], [[pred]], axis=0)

forecasted = scaler.inverse_transform(np.array(forecasted).reshape(-1, 1))

# --- Affichage ---
plt.figure(figsize=(14, 6))

# Historique Close réel
plt.plot(df['date'], close_prices, label='Prix BTC réel')

# Prédiction test (sur dernière partie)
test_dates = df['date'].iloc[train_size+SEQ_LENGTH : train_size+SEQ_LENGTH+len(y_test)]
plt.plot(test_dates, y_pred, label='Prédictions LSTM (test)', linestyle='--')

# Forecast futur 15 jours
last_date = df['date'].iloc[-1]
forecast_dates = [last_date + pd.Timedelta(days=i) for i in range(1, 16)]
plt.plot(forecast_dates, forecasted, label='Prévisions LSTM 15 jours', linestyle='--')

plt.title('Prédiction prix BTC avec LSTM')
plt.xlabel('Date')
plt.ylabel('Prix Close (USD)')
plt.legend()
plt.grid(True)
plt.show()
