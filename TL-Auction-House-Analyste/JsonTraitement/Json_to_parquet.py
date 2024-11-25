import time
import numpy as np
import pandas as pd
import json

# Fonction pour charger et traiter le fichier JSON
def process_json_to_parquet(input_file, output_file):
    # Charger le fichier JSON
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Accéder aux données de la liste
    list_data = data['list']

    # Créer une liste pour stocker les lignes de données
    records = []

    # Extraire les données

    for server_id, items in list_data.items():
        print(server_id)
        for item_id, item_data in items.items():
            quantity = item_data['quantity']
            print(quantity)
            sales = item_data['sales']
            for sale in sales:
                item_trait = sale.get('t', None)

                if item_trait is None:
                    item_trait = np.nan

                records.append({
                    'server_id': server_id,
                    'item_id': item_id,
                    'quantity_on_market': quantity,
                    'sale_quantity': sale['c'],
                    'sale_price': sale['p'],
                    'item_trait': item_trait
                })

    # Convertir en DataFrame Pandas
    df = pd.DataFrame(records)

    # Enregistrer le DataFrame en format Parquet
    df.to_parquet(output_file, engine='pyarrow', compression='snappy')

    print(f"Le fichier Parquet a été créé avec succès : {output_file}")

# Exemple d'appel de la fonction avec un fichier JSON en entrée et un fichier Parquet en sortie
input_file = 'data.json'  # Chemin vers votre fichier JSON d'entrée
output_file = 'sales_data.parquet'  # Nom du fichier Parquet de sortie

process_json_to_parquet(input_file, output_file)
