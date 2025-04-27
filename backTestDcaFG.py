import pandas as pd
import matplotlib.pyplot as plt

# Load your data
df = pd.read_csv('data.csv', parse_dates=['Date'])
df = df.set_index('Date')

# Initial conditions
cash = 0      # Cash available from sells
btc_holdings = 0.0
investment_per_day = 10  # 10€ per day
cash_invested = 0  # Track how much money we invested

# To track performance
history = []

# Simulation
for date, row in df.iterrows():
    close_price = row['Close']
    fgi_value = row['fgi_value']

    if fgi_value < 60:
        # BUY 10€ worth of BTC
        btc_bought = investment_per_day / close_price
        btc_holdings += btc_bought
        cash -= investment_per_day
        cash_invested += investment_per_day
        action = f"BUY 10€ of BTC at {close_price:.2f}"
    else:
        if btc_holdings > 0:
            # SELL 10€ worth of BTC, or all if not enough
            btc_to_sell = investment_per_day / close_price
            if btc_to_sell > btc_holdings:
                btc_to_sell = btc_holdings
            sell_value = btc_to_sell * close_price
            btc_holdings -= btc_to_sell
            cash += sell_value
            action = f"SELL {sell_value:.2f}€ of BTC"
        else:
            action = "HOLD (no BTC to sell)"

    # Portfolio value = Cash available + BTC value
    btc_value = btc_holdings * close_price
    portfolio_value = cash + btc_value
    equity = portfolio_value + cash_invested  # Equity = Portfolio Value + Cash Invested

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

# Create final DataFrame
final_df = pd.DataFrame(history)
final_df.set_index('Date', inplace=True)

# Save result to CSV
final_df.to_csv('backtest_result.csv')

# Results
final_value = final_df.iloc[-1]['Portfolio Value']
total_invested = final_df.iloc[-1]['Cash Invested']

print("\n🔔 Final Result:")
print(f"Final Portfolio Value: {final_value:.2f}€")
print(f"Total Cash Invested: {total_invested:.2f}€")
print(f"Profit: {(final_value - total_invested):.2f}€")

# --- Plot ---
plt.figure(figsize=(16, 9))

# Plot lines
plt.plot(final_df.index, final_df['Cash Invested'], label='💶 Cash Invested', color='blue')
plt.plot(final_df.index, final_df['Equity'], label='🏦 Equity (Portfolio Value + Cash Invested)', color='purple', linestyle='--')

# Plot buy/sell markers on the Equity line
buy_signals = final_df[final_df['Action'].str.contains('BUY')]
sell_signals = final_df[final_df['Action'].str.contains('SELL')]

plt.scatter(buy_signals.index, buy_signals['Equity'], label='🟢 Buy', marker='^', color='lime', s=100)
plt.scatter(sell_signals.index, sell_signals['Equity'], label='🔴 Sell', marker='v', color='red', s=100)

# Decorations
plt.title('Backtest: Invest 10€/day if FGI < 60, Sell 10€/day if FGI >= 60')
plt.xlabel('Date')
plt.ylabel('€ Value')
plt.legend()
plt.grid(True)
plt.tight_layout()

# Show plot
plt.show()
