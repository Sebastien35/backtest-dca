import pandas as pd

input_file = "btcusd_1-min_data" \
".csv"   # Ton fichier énorme
output_file = "daily_close.csv"

chunksize = 10**6  # 1 million de lignes à la fois

daily_close = {}

for chunk in pd.read_csv(input_file, chunksize=chunksize):
    # Convertir timestamp en datetime date
    chunk['date'] = pd.to_datetime(chunk['Timestamp'], unit='s').dt.date
    
    # Pour chaque date dans ce chunk, prendre la dernière valeur Close (en supposant que les lignes sont triées)
    grouped = chunk.groupby('date')['Close'].last()
    
    # Mettre à jour le dictionnaire global (en gardant la dernière Close disponible)
    for date, close in grouped.items():
        daily_close[date] = close

# Transformer en DataFrame et sauvegarder
df_daily = pd.DataFrame(list(daily_close.items()), columns=['date', 'Close']).sort_values('date')
df_daily.to_csv(output_file, index=False)

print(f"Fichier quotidien créé : {output_file}")
