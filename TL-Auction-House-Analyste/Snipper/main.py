import csv
import os
from collections import defaultdict
import json
import time
from datetime import datetime

import pygame


def process_csv(input_file, data_file, output_brute_file, output_profit_file, servers, percentage_threshold=20, cost_threshold=150, depth=10, instant_profit_threshold=10):
    """
    Process the input CSV to calculate profitability at different depths for each name and trait.
    Then filter the results based on a given profitability threshold and cost threshold.

    Parameters:
    - input_file: Path to the input CSV.
    - output_brute_file: Path to the raw output CSV containing detailed profitability results.
    - output_profit_file: Path to the filtered output CSV containing results based on thresholds.
    - percentage_threshold: Minimum profitability percentage to be considered for output_profit.csv.
    - cost_threshold: Minimum cost to be considered for output_profit.csv.
    - depth: Maximum depth to calculate profitability for (+1 to +10).
    """
    # Lecture des données à partir du fichier JSON
    with open(input_file, 'r', encoding='utf-8') as infile:
        data = json.load(infile)

    with open(data_file, 'r', encoding='utf-8') as infile:
        data_name = json.load(infile)

    # Préparer les résultats bruts
    brute_results = []

    # Processus pour chaque serveur
    for server in servers:
        if str(server) not in data["list"]:
            print(f"Le serveur {server} n'existe pas dans le fichier.")
            continue

        server_data = data["list"][str(server)]
        grouped_data = []

        # Parcours des items
        for item_id, item_data in server_data.items():
            sales = item_data.get("sales", [])

            # Si le premier élément contient un trait
            if 't' in sales[0]:
                # Création d'un dictionnaire des ventes par trait pour éviter des boucles imbriquées
                trait_sales = {}
                for sale in sales:
                    trait = sale.get('t')
                    if trait:
                        if trait not in trait_sales:
                            trait_sales[trait] = []
                        sale_copy = sale.copy()  # On copie l'élément avant de supprimer le trait
                        sale_copy.pop('t', None)  # Retirer 't' de la copie
                        trait_sales[trait].append(sale_copy)

                # Ajout des données traitées pour chaque trait
                for trait, data in trait_sales.items():
                    grouped_data.append((item_id, str(trait), data))

            else:
                # Si aucun trait, on ajoute la donnée sans transformation
                grouped_data.append((item_id, "NULL", sales))

    for name, trait, rows in grouped_data:
        if len(rows) < 5:  # Si moins de 15 items, on ignore ce groupe
            continue
            # Trier les prix par ordre croissant
        rows.sort(key=lambda x: x['p'])  # Tri par prix croissant

        # Liste des prix
        prices = [(row['p'], row['c']) for row in rows]

        # Calculer les résultats pour chaque profondeur de 1 à 10
        for depth_incr in range(0, depth + 1):
            if len(prices) < depth_incr + 1:
                continue  # Si on n'a pas assez de prix pour cette profondeur

            # Calcul du coût total pour cette profondeur (coût des `depth_incr` premiers items)
            total_cost = 0
            if depth_incr != 0:
                for p, c in prices[:depth_incr]:
                    total_cost += p * c

            # Calcul du profit pour cette profondeur : vente des `depth_incr` items suivants
            if depth_incr < len(prices):
                if depth_incr == 0:
                    sale_revenue = 0
                    instant_profit = 0
                    profitability = 0
                else:
                    sale_revenue = prices[depth_incr][0] * 0.77 * depth_incr   # Vendre au prix de l'élément suivant après achat
                    instant_profit = sale_revenue - total_cost  # Rentabilité après taxe

                    # Rentabilité en pourcentage
                    profitability = (instant_profit / total_cost) * 100  # Rentabilité en pourcentage

                temp_name = name

                for info in data_name['items']:
                    if info['num'] == int(name):
                        temp_name = info['name']

                temp_trait = trait

                if trait != "NULL":
                    temp_trait = data_name['traits'][trait]['name']

                brute_results.append({
                    'Name': temp_name,
                    'Trait': temp_trait,
                    'Depth': depth_incr,
                    'Cost': total_cost,
                    'Instant Profit': round(instant_profit, 2),
                    'Profitability (%)': int(round(profitability, 2)),
                    'Item Price': prices[depth_incr][0],  # Prix de l'item étudié (celui sur lequel on base la rentabilité)
                    'Occurrences': len(rows),
                    'Sale Price': prices[depth_incr + 1][0]  # Prix de vente théorique (prix de l'item suivant)
                })

    # Enregistrement du fichier raw (output_brute.csv)
    with open(output_brute_file, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile, delimiter=';')
        writer.writerow(
            ['Name', 'Trait', 'Depth', 'Cost (total)', 'Instant Profit', 'Profitability (%)', 'Item Price (par u)',
             'Sale Price (par u)', 'Occurrences'])
        for result in brute_results:
            writer.writerow([
                result['Name'],
                result['Trait'],
                result['Depth'],
                result['Cost'],
                result['Instant Profit'],
                result['Profitability (%)'],
                result['Item Price'],
                result['Sale Price'],
                result['Occurrences']
            ])

    # Filtrage des résultats par rentabilité et coût, et enregistrement du fichier final (output_profit.csv)
    filtered_results = [result for result in brute_results if
                        result['Profitability (%)'] >= percentage_threshold and result[
                            'Cost'] <= cost_threshold and result['Instant Profit'] > 12]

    for result in filtered_results:
        print(result)

    with open(output_profit_file, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile, delimiter=';')
        writer.writerow(
            ['Name', 'Trait', 'Depth', 'Cost', 'Instant Profit', 'Profitability (%)', 'Sale Price',
             'Occurrences'])
        for result in filtered_results:
            writer.writerow([
                result['Name'],
                result['Trait'],
                result['Depth'],
                result['Cost'],
                result['Instant Profit'],
                result['Profitability (%)'],
                result['Sale Price'],
                result['Occurrences']
            ])
            
            
while True:
    now = datetime.now()
    # Vérifie si la seconde est '01'
    if now.second >= 0:
        # Chemin vers ton fichier JS
        js_file = 'test.js'

        # Exécution du fichier JS avec Node.js
        os.system(f'E:/ProgramationPerso/NodeJS/node.exe {js_file}')

        pygame.mixer.init()

        # Charger le fichier audio
        son = pygame.mixer.Sound("son.mp3")

        # Régler le volume à 50%
        son.set_volume(0.5)  # 0.5 représente 50% du volume maximum

        # Jouer le son
        #son.play()

        # Exemple d'utilisation
        process_csv(
            'item_prices_data.json',
            'auction_house_data.json',
            'output_brute.csv',
            'output_profit.csv',
            servers=['30001'],
            percentage_threshold=50,  # Rentabilité minimum en %
            cost_threshold=2000,  # Coût maximum
            depth=3,  # Profondeur maximale de 10
            instant_profit_threshold = 12
    )
    else:
        time.sleep(0.5)