import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt

# --- Load and prepare data ---
df = pd.read_csv("data.csv")
df.columns = df.columns.str.strip()
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").dropna(subset=["Close", "fgi_value"])
df["Days"] = (df["date"] - df["date"].min()).dt.days

# --- Backtest to find best polynomial degree ---
window_size = 85
future_days = 3
best_degree = None
best_rmse = float('inf')

best_backtest_dates = []
best_backtest_real_prices = []
best_backtest_pred_prices = []

for degree in range(1, 9):
    real_prices = []
    pred_prices = []
    dates_real = []

    # Backtest sur toute la période possible (à partir de window_size)
    for i in range(window_size, len(df) - future_days):
        df_train = df.iloc[:i]
        df_test = df.iloc[i:i + future_days]

        X_train = df_train[["Days", "fgi_value"]]
        y_train = df_train["Close"]

        X_test = df_test[["Days", "fgi_value"]]
        y_test = df_test["Close"]

        model = make_pipeline(PolynomialFeatures(degree), LinearRegression())
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        real_prices.extend(y_test.tolist())
        pred_prices.extend(y_pred.tolist())
        dates_real.extend(df_test["date"].tolist())

    if len(real_prices) == 0:
        print(f"Pas assez de données pour degré {degree} avec window_size {window_size}")
        continue

    rmse = np.sqrt(mean_squared_error(real_prices, pred_prices))
    print(f"Degré {degree} - RMSE: {rmse:.4f}")

    if rmse < best_rmse:
        best_rmse = rmse
        best_degree = degree
        best_backtest_dates = dates_real
        best_backtest_real_prices = real_prices
        best_backtest_pred_prices = pred_prices

print(f"\n✅ Meilleur degré polynomial trouvé : {best_degree} avec RMSE = {best_rmse:.4f}")

# --- Forecast next 15 days ---
forecast_days = 15
forecasted_dates = []
forecasted_prices = []

df_full = df.copy()

for _ in range(forecast_days):
    last_day = df_full["Days"].iloc[-1]
    next_day = last_day + 1
    next_date = df_full["date"].iloc[-1] + pd.Timedelta(days=1)
    next_fgi = df_full["fgi_value"].iloc[-1]

    model = make_pipeline(PolynomialFeatures(best_degree), LinearRegression())
    model.fit(df_full[["Days", "fgi_value"]], df_full["Close"])

    next_X = pd.DataFrame({"Days": [next_day], "fgi_value": [next_fgi]})
    price_pred = model.predict(next_X)[0]

    forecasted_dates.append(next_date)
    forecasted_prices.append(price_pred)

    df_full = pd.concat([df_full, pd.DataFrame({
        "date": [next_date],
        "Days": [next_day],
        "fgi_value": [next_fgi],
        "Close": [price_pred]
    })], ignore_index=True)

# --- Save backtest results to CSV ---
backtest_df = pd.DataFrame({
    "date": best_backtest_dates,
    "real_Close": best_backtest_real_prices,
    "pred_Close": best_backtest_pred_prices
})
backtest_df.to_csv("backtest_results.csv", index=False)

# --- Save forecast results to CSV ---
forecast_df = pd.DataFrame({
    "date": forecasted_dates,
    "forecasted_Close": forecasted_prices
})
forecast_df.to_csv("forecast_results.csv", index=False)

# --- Plotting main results ---
plt.figure(figsize=(14, 6))
plt.plot(df["date"], df["Close"], label="Prix réel BTC", color="black", alpha=0.7)
plt.plot(best_backtest_dates, best_backtest_pred_prices, label="Prévisions backtest", color="blue", linestyle="--")
plt.plot(forecasted_dates, forecasted_prices, label=f"Prévisions futures ({forecast_days} jours)", color="red", linestyle="--")
plt.scatter(forecasted_dates, forecasted_prices, color="red", s=40)
plt.axvline(df["date"].iloc[-1], color="gray", linestyle=":", label="Début prévision")
plt.title(f"Prix BTC réel, backtest & prévisions futures (degré {best_degree})")
plt.xlabel("Date")
plt.ylabel("Prix BTC (USD)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# --- Performance metrics on backtest ---
rmse_backtest = np.sqrt(mean_squared_error(best_backtest_real_prices, best_backtest_pred_prices))
mae_backtest = mean_absolute_error(best_backtest_real_prices, best_backtest_pred_prices)

print(f"\n📊 Performance backtest :")
print(f"RMSE = {rmse_backtest:.4f}")
print(f"MAE  = {mae_backtest:.4f}")

# --- Plot backtest real vs predicted ---
plt.figure(figsize=(14, 6))
plt.plot(best_backtest_dates, best_backtest_real_prices, label="Prix réel (backtest)", color="black")
plt.plot(best_backtest_dates, best_backtest_pred_prices, label="Prix prédit (backtest)", color="blue", linestyle="--")
plt.title(f"Comparaison backtest : réel vs prédit (degré {best_degree})")
plt.xlabel("Date")
plt.ylabel("Prix BTC (USD)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
