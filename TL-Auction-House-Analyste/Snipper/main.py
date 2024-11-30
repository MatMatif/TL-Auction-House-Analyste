import json
import requests
import time
import numpy as np
from compress_json import decompress
import hashlib
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout,
                             QGridLayout, QTreeWidget, QTreeWidgetItem, QHeaderView)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QColor


class DataFetcher(QThread):
    data_ready = pyqtSignal(dict, float)

    def __init__(self, server):
        super().__init__()
        self.server = server

    def run(self):
        start_time = time.time()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        url = "https://tldb.info/api/ah/prices"
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()
            list_data = data["list"]
            fetched_data = decompress(json.loads(list_data[self.server]))
            end_time = time.time()
            latency = end_time - start_time
            self.data_ready.emit(fetched_data, latency)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            self.data_ready.emit(None, 0) # Emit None to signal error


class DataProcessor:
    def process_data(self, data, data_name, percentage_threshold, cost_threshold, depth, mini_profit=10):
        brute_results = []


        grouped_data = []
        # Parcours des items
        for item_id, item_data in data.items():
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
                        sale_revenue = prices[depth_incr][
                                           0] * 0.77 * depth_incr  # Vendre au prix de l'élément suivant après achat
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
                        'Item Price': prices[depth_incr][0],
                        # Prix de l'item étudié (celui sur lequel on base la rentabilité)
                        'Occurrences': len(rows),
                        'Sale Price': prices[depth_incr + 1][0]  # Prix de vente théorique (prix de l'item suivant)
                    })

        # Optimisation: Filtrage avec une liste de compréhension et conditions combinées
        filtered_results = [result for result in brute_results if
                            result['Profitability (%)'] >= percentage_threshold and result['Cost'] <= cost_threshold and
                            result[
                                'Instant Profit'] > 4]
        filtered_results.sort(key=lambda x: x['Instant Profit'], reverse=True)
        return filtered_results

    def generate_item_id(self, item):
        hash_string = f"{item['Name']}{item['Trait']}"
        return hashlib.md5(hash_string.encode()).hexdigest()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Affichage des Résultats")
        self.data_processor = DataProcessor()
        self.percentage_threshold = 20
        self.cost_threshold = 3000
        self.depth = 1
        self.mini_profit = 10
        self.last_top_id = None
        self.server = "30001"
        self.initUI()
        self.data_name = self.load_data_name("auction_house_data.json")
        self.start_refresh()

    def load_data_name(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as infile:
                return json.load(infile)
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return {}


    def initUI(self):
        grid = QGridLayout()

        # Input fields
        grid.addWidget(QLabel("Profit minimum"), 0, 0)
        self.percentage_edit = QLineEdit(str(self.mini_profit))
        self.percentage_edit.textChanged.connect(self.update_thresholds)
        grid.addWidget(self.percentage_edit, 0, 1)

        grid.addWidget(QLabel("Seuil de Coût"), 1, 0)
        self.cost_edit = QLineEdit(str(self.cost_threshold))
        self.cost_edit.textChanged.connect(self.update_thresholds)
        grid.addWidget(self.cost_edit, 1, 1)

        grid.addWidget(QLabel("Profondeur"), 2, 0)
        self.depth_edit = QLineEdit(str(self.depth))
        self.depth_edit.textChanged.connect(self.update_thresholds)
        grid.addWidget(self.depth_edit, 2, 1)

        self.latency_label = QLabel("Latence: ")
        grid.addWidget(self.latency_label, 3, 0, 1, 2)

        # Tree Widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Name", "Trait", "Depth", "Cost", "Instant Profit", "Profitability (%)", "Item Price", "Occurrences", "Sale Price"])
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tree.itemClicked.connect(self.on_item_clicked)
        grid.addWidget(self.tree, 4, 0, 1, 2)

        self.setLayout(grid)



    def update_thresholds(self):
        try:
            self.percentage_threshold = int(self.percentage_edit.text())
            self.cost_threshold = int(self.cost_edit.text())
            self.depth = int(self.depth_edit.text())
        except ValueError:
            pass  # Ignore invalid input


    def start_refresh(self):
        self.fetcher = DataFetcher(self.server)
        self.fetcher.data_ready.connect(self.update_gui)
        self.fetcher.start()


    def update_gui(self, data, latency):
        if data is None:
          self.latency_label.setText(f"Latence: Erreur lors de la récupération des données")
          return

        results = self.data_processor.process_data(data, self.data_name, self.percentage_threshold, self.cost_threshold, self.depth, self.mini_profit)
        self.latency_label.setText(f"Latence: {latency:.4f} secondes")
        self.tree.clear()
        for result in results:
            item = QTreeWidgetItem(self.tree)
            item.setText(0, result['Name'])
            item.setText(1, result['Trait'])
            item.setText(2, str(result['Depth']))
            item.setText(3, str(result['Cost']))
            item.setText(4, str(result['Instant Profit']))
            item.setText(5, str(result['Profitability (%)']))
            item.setText(6, str(result['Item Price']))
            item.setText(7, str(result['Occurrences']))
            item.setText(8, str(result['Sale Price']))
            profitability = min(result['Instant Profit'], 1000)
            color = self.get_color(profitability)
            item.setBackground(0, QColor(color))

            for i in range(self.tree.columnCount()):
                item.setBackground(i, self.get_color(profitability))

        self.start_refresh() #restart the fetcher

    def get_color(self, profitability):
        profitability = min(profitability, 1000)  # Cap at 1000

        if profitability <= 100:
            # Linear interpolation from (50, 255, 50) to (255, 255, 50)
            normalized_p = profitability / 100.0
            r = int(50 + (255 - 50) * normalized_p)
            g = 255
            b = 50
        else:
            # Linear interpolation from (255, 255, 50) to (255, 50, 50)
            normalized_p = (profitability - 100) / 900.0  # Normalize to 0-1 range for 100-1000
            r = 255
            g = int(255 - (255 - 50) * normalized_p)
            b = 50

        return QColor(r, g, b)

    def on_item_clicked(self, item, column):
        if column == 0:
            name = item.text(0)
            QApplication.clipboard().setText(name)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())