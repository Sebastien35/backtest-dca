import pandas as pd
import matplotlib.pyplot as plt

# --- Prompt user for variables ---
print("\n🛠️  Configuration du backtest")

csv_file = input("Nom du fichier CSV (ex: data.csv) : ").strip() or "data.csv"
investment_per_day = float(input("Montant à investir par jour (€) (ex: 10) : ") or 10)
fgi_threshold = int(input("Seuil FGI pour acheter (<) ou vendre (>=) (ex: 60) : ") or 60)

print("\n▶️  Démarrage du backtest...\n")

# --- Load Data ---
df = pd.read_csv(csv_file, parse_dates=['Date'])
df = df.set_index('Date')

# --- Initial conditions ---
cash = 0
btc_holdings = 0.0
cash_invested = 0

history = []

# --- Simulation ---
for date, row in df.iterrows():
    close_price = row['Close']
    fgi_value = row['fgi_value']

    if fgi_value < fgi_threshold:
        # BUY
        btc_bought = investment_per_day / close_price
        btc_holdings += btc_bought
        cash -= investment_per_day
        cash_invested += investment_per_day
        action = f"BUY {investment_per_day}€ of BTC at {close_price:.2f}"
    else:
        if btc_holdings > 0:
            # SELL
            btc_to_sell = investment_per_day / close_price
            if btc_to_sell > btc_holdings:
                btc_to_sell = btc_holdings
            sell_value = btc_to_sell * close_price
            btc_holdings -= btc_to_sell
            cash += sell_value
            action = f"SELL {sell_value:.2f}€ of BTC"
        else:
            action = "HOLD (no BTC to sell)"

    btc_value = btc_holdings * close_price
    portfolio_value = cash + btc_value
    equity = portfolio_value + cash_invested

    history.append({
        'Date': date,
        'Cash': cash,
        'BTC Holdings': btc_holdings,
        'BTC Price': close_price,
        'BTC Value': btc_value,
        'Portfolio Value': portfolio_value,
        'Cash Invested': cash_invested,
        'Equity': equity,
        'Action': action
    })

# --- Final Data ---
final_df = pd.DataFrame(history)
final_df.set_index('Date', inplace=True)

# Save result
result_filename = 'backtest_result.csv'
final_df.to_csv(result_filename)

# --- Results ---
final_value = final_df.iloc[-1]['Portfolio Value']
total_invested = final_df.iloc[-1]['Cash Invested']

print("\n🔔 Résultat Final :")
print(f"Valeur Finale du Portfolio : {final_value:.2f}€")
print(f"Cash Investi Total : {total_invested:.2f}€")
print(f"Profit : {(final_value - total_invested):.2f}€")
print(f"(Données enregistrées dans {result_filename})")

# --- Plot ---
plt.figure(figsize=(16, 9))

plt.plot(final_df.index, final_df['Cash Invested'], label='💶 Cash Invested', color='blue')
plt.plot(final_df.index, final_df['Equity'], label='🏦 Equity (Portfolio Value + Cash Invested)', color='purple', linestyle='--')

buy_signals = final_df[final_df['Action'].str.contains('BUY')]
sell_signals = final_df[final_df['Action'].str.contains('SELL')]

plt.scatter(buy_signals.index, buy_signals['Equity'], label='🟢 Buy', marker='^', color='lime', s=100)
plt.scatter(sell_signals.index, sell_signals['Equity'], label='🔴 Sell', marker='v', color='red', s=100)

plt.title(f'Backtest: Invest {investment_per_day}€/day if FGI < {fgi_threshold}, Sell otherwise')
plt.xlabel('Date')
plt.ylabel('€ Value')
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.show()
