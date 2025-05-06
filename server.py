from flask import Flask, jsonify, request
from getCryptoArticles import getNewsArticles
from processArticles import process_articles

import pandas as pd

app = Flask(__name__)

@app.route('/simulate', methods=['GET'])
def simulate():
    try:
        daily_investment = float(request.args.get('daily_investment', 10))
        df = pd.read_csv("data.csv", parse_dates=['date'])

        btc_accumulated = 0.0
        total_invested = 0.0

        for _, row in df.iterrows():
            close_price = row['Close']
            if pd.notna(close_price) and close_price > 0:
                btc_bought = daily_investment / close_price
                btc_accumulated += btc_bought
                total_invested += daily_investment

        final_price = df.iloc[-1]['Close']
        final_value = btc_accumulated * final_price
        profit = final_value - total_invested

        return jsonify({
            'daily_investment_eur': daily_investment,
            'days': len(df),
            'total_invested_eur': round(total_invested, 2),
            'btc_accumulated': round(btc_accumulated, 6),
            'final_btc_price': round(final_price, 2),
            'final_value_eur': round(final_value, 2),
            'profit_eur': round(profit, 2)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/news', methods=['GET'])
def getNews():
    try:
        data = getNewsArticles()
        df = process_articles('blockchain_news.csv')
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)