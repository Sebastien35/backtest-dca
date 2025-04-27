import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta

# Step 1: Download BTC price data
ticker = 'BTC-USD'
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

btc_data = yf.download(
    ticker,
    start=start_date.strftime('%Y-%m-%d'),
    end=end_date.strftime('%Y-%m-%d'),
    interval='1d'
)

btc_data.index = pd.to_datetime(btc_data.index).normalize()

# 🔥 Flatten column names if MultiIndex
if isinstance(btc_data.columns, pd.MultiIndex):
    btc_data.columns = [' '.join(col).strip() for col in btc_data.columns]

# Step 2: Fetch Fear and Greed Index data
fgi_response = requests.get('https://api.alternative.me/fng/?limit=60&format=json')
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

# Step 3: Merge BTC data with FGI data
merged = btc_data.join(fgi_df, how='left')

# 🔥 Detect Close column
close_column = next((col for col in merged.columns if 'Close' in col), None)

if close_column is None:
    raise ValueError("❌ Couldn't find a Close column!")

# Keep only Close, fgi_value, fgi_classification
merged = merged[[close_column, 'fgi_value', 'fgi_classification']]
merged = merged.rename(columns={close_column: 'Close'})

# Step 4: Save to CSV
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
csv_filename = "data.csv"
merged.to_csv(csv_filename)

print(f"✅ Merged BTC + FGI data saved to {csv_filename}")
