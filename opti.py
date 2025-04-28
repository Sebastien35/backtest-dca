import pandas as pd

def run_backtest(df, investment_per_day, fgi_threshold, sell_amount):
    cash = 0
    btc_holdings = 0.0
    cash_invested = 0.0

    for date, row in df.iterrows():
        close_price = row['Close']
        fgi_value = row['fgi_value']

        # Deposit money every day
        cash += investment_per_day

        if fgi_value < fgi_threshold:
            # Buy BTC if FGI is below threshold
            if cash >= investment_per_day:
                btc_bought = investment_per_day / close_price
                btc_holdings += btc_bought
                cash -= investment_per_day
                cash_invested += investment_per_day
        else:
            # Sell BTC if FGI is high
            if btc_holdings > 0:
                btc_to_sell = sell_amount / close_price
                if btc_to_sell > btc_holdings:
                    btc_to_sell = btc_holdings
                sell_value = btc_to_sell * close_price
                btc_holdings -= btc_to_sell
                cash += sell_value

    # Final portfolio value
    btc_value = btc_holdings * df.iloc[-1]['Close']
    final_portfolio_value = cash + btc_value
    profit = final_portfolio_value - cash_invested

    return final_portfolio_value, cash_invested, profit

def main():
    print("▶️  Chargement des données...")

    filename = "data.csv"

    try:
        df = pd.read_csv(filename, parse_dates=['Date'])
        df.set_index('Date', inplace=True)
    except Exception as e:
        print(f"Erreur lors du chargement du fichier : {e}")
        return

    investment_per_day = 10  # € investis par jour
    fgi_thresholds = range(10, 95, 5)  # De 10 à 90 inclus
    sell_amounts = [10, 20, 30]  # Montants fixes de vente

    best_result = {
        'final_value': 0,
        'fgi_threshold': None,
        'sell_amount': None,
        'cash_invested': None,
        'profit': None
    }

    print("\n🔍 Démarrage des tests de combinaisons...\n")

    for fgi_threshold in fgi_thresholds:
        for sell_amount in sell_amounts:
            final_value, cash_invested, profit = run_backtest(df, investment_per_day, fgi_threshold, sell_amount)

            print(f"Test: FGI Threshold={fgi_threshold}, Sell Amount={sell_amount}€ => "
                  f"Final Equity: {final_value:.2f}€, Cash Invested: {cash_invested:.2f}€, Profit: {profit:.2f}€")

            if final_value > best_result['final_value']:
                best_result.update({
                    'final_value': final_value,
                    'fgi_threshold': fgi_threshold,
                    'sell_amount': sell_amount,
                    'cash_invested': cash_invested,
                    'profit': profit
                })

    print("\n🏆 Meilleure configuration trouvée :")
    print(f"Seuil FGI : {best_result['fgi_threshold']}")
    print(f"Montant à vendre : {best_result['sell_amount']}€")
    print(f"Valeur finale du portfolio : {best_result['final_value']:.2f}€")
    print(f"Cash investi total : {best_result['cash_invested']:.2f}€")
    print(f"Profit (portefeuille - investissement) : {best_result['profit']:.2f}€")

if __name__ == "__main__":
    main()
