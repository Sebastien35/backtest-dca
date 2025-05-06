import pandas as pd
import requests
from datetime import datetime, timedelta

end_date = datetime.now()
start_date = end_date - timedelta(days=90)

vs_currency = 'usd'
days = 90

price_url = f'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart'
params = {
    'vs_currency': vs_currency,
    'days': days,
    'interval': 'daily'
}

price_response = requests.get(price_url, params=params)
price_data = price_response.json()['prices']

btc_df = pd.DataFrame(price_data, columns=['timestamp', 'Close'])
btc_df['timestamp'] = pd.to_datetime(btc_df['timestamp'], unit='ms')
btc_df['date'] = btc_df['timestamp'].dt.normalize()
btc_df.set_index('date', inplace=True)
btc_df = btc_df[['Close']]

fgi_response = requests.get('https://api.alternative.me/fng/?limit=90&format=json')
fgi_data = fgi_response.json()['data']

fgi_df = pd.DataFrame([
    {
        'date': datetime.fromtimestamp(int(item['timestamp'])).date(),
        'fgi_value': int(item['value']),
        'fgi_classification': item['value_classification']
    }
    for item in fgi_data
])
fgi_df.set_index('date', inplace=True)
fgi_df.index = pd.to_datetime(fgi_df.index)

merged = btc_df.join(fgi_df, how='left')

timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
csv_filename = "data.csv"
merged.to_csv(csv_filename)

print(f"✅ Merged BTC + FGI data saved to {csv_filename}")
