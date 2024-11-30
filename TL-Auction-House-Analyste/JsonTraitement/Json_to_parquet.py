import time
import numpy as np
import pandas as pd
import json

# Fonction pour charger et traiter le fichier JSON
def process_json_to_parquet(input_data_file, input_price_file, output_file):
    # Charger le fichier JSON
    with open(input_price_file, 'r') as f, open(input_data_file, 'r') as y:
        price = json.load(f)
        data = json.load(y)
    
    # Accéder aux données de la liste
    list_price = price['list']
    list_data = data['items']
    # Créer une liste pour stocker les lignes de données
    records = []
    item_data = {item['num']: item['name'] for item in list_data if item['num'] and item['name']}

    print(item_data)
    # Extraire les données

    for server_id, items in list_price.items():
        #print(server_id)
        for item_id, item_price in items.items():
            quantity = item_price['quantity']
            #print(quantity)
            sales = item_price['sales']
            for sale in sales:
                item_trait = sale.get('t', np.nan)

                item_num = int(item_id)
                item_name = item_data.get(item_num, "Unknown")
                records.append({
                    's_id': server_id,
                    #'item_id': item_id,
                    'i_name': item_name,
                    #'quantity_on_market': quantity,
                    's_q': sale['c'],
                    's_p': sale['p'],
                    'i_t': item_trait
                })

    # Convertir en DataFrame Pandas
    df = pd.DataFrame(records)

    # Enregistrer le DataFrame en format Parquet
    df.to_parquet(output_file, engine='pyarrow', compression='snappy')

    print(f"Le fichier Parquet a été créé avec succès : {output_file}")

# Exemple d'appel de la fonction avec un fichier JSON en entrée et un fichier Parquet en sortie
input_price_file = 'data/item_prices/item_prices_data_2024-11-24T17_52_03.878Z.json'  # Chemin vers votre fichier JSON d'entrée
input_data_file = 'data/auction_house/auction_house_data_2024-11-24T17_54_01.994Z.json'
output_file = 'sales_price.parquet'  # Nom du fichier Parquet de sortie

process_json_to_parquet(input_data_file, input_price_file, output_file)
