import json
import threading
import hashlib
import pickle
import datetime
import sys
from dataclasses import dataclass
from typing import Optional

import requests
import time
import pyperclip
from compress_json import decompress

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout,
                             QGridLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QHeaderView, QMessageBox,
                             QInputDialog)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

MAX_PRICE = 999999999

@dataclass
class Item:
    name: str
    bought: float
    sold: Optional[float] = 0.0
    timestamp: str = ""


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
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            list_data = data["list"]
            fetched_data = decompress(json.loads(list_data[self.server]))
            end_time = time.time()
            latency = end_time - start_time
            self.data_ready.emit(fetched_data, latency)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            self.data_ready.emit({}, 0)
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"Error processing API response: {e}")
            self.data_ready.emit({}, 0)


class DataProcessor:
    def process_data(self, data, data_name, percentage_threshold, cost_threshold, depth, mini_profit):
        if not data_name or not data_name.get('items') or not data_name.get('traits'):
            return [] # Return empty list if data_name is invalid

        brute_results = []
        grouped_data = []
        for item_id, item_data in data.items():
            sales = item_data.get("sales", [])
            if 't' in sales[0]:
                trait_sales = {}
                for sale in sales:
                    trait = sale.get('t')
                    if trait:
                        if trait not in trait_sales:
                            trait_sales[trait] = []
                        sale_copy = sale.copy()
                        sale_copy.pop('t', None)
                        trait_sales[trait].append(sale_copy)
                for trait, data in trait_sales.items():
                    grouped_data.append((item_id, str(trait), data))
            else:
                grouped_data.append((item_id, "NULL", sales))

        for name, trait, rows in grouped_data:
            if len(rows) < 5:
                continue
            rows.sort(key=lambda x: x['p'])
            prices = [(row['p'], row['c']) for row in rows]
            for depth_incr in range(1, depth + 1): #Start from 1 to avoid unnecessary calculation when depth_incr is 0
                if len(prices) < depth_incr + 1:
                    continue
                total_cost = sum(p * c for p, c in prices[:depth_incr])
                sale_revenue = prices[depth_incr][0] * 0.77 * depth_incr
                instant_profit = sale_revenue - total_cost
                profitability = (instant_profit / total_cost) * 100 if total_cost > 0 else 0 #Handle division by zero

                temp_name = name
                for info in data_name['items']:
                    if info['num'] == int(name):
                        temp_name = info['name']

                temp_trait = trait
                if trait != "NULL":
                    temp_trait = data_name['traits'][trait]['name']

                sale_price = prices[depth_incr][0] if depth_incr < len(prices) else -1

                brute_results.append({
                    'Name': temp_name,
                    'Trait': temp_trait,
                    'Depth': depth_incr,
                    'Cost': total_cost,
                    'Instant Profit': round(instant_profit, 2),
                    'Profitability (%)': int(round(profitability, 2)),
                    'Item Price': prices[depth_incr -1][0], #Adjusted index to access correct price
                    'Occurrences': len(rows),
                    'Sale Price': sale_price
                })

        filtered_results = [result for result in brute_results if
                            result['Profitability (%)'] >= percentage_threshold and result['Cost'] <= cost_threshold and
                            result['Instant Profit'] >= mini_profit]
        filtered_results.sort(key=lambda x: x['Instant Profit'], reverse=True)
        return filtered_results


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Log des Achats et Analyse des Items")
        self.filename = "achat_data.pickle"
        self.items = []
        self.data_processor = DataProcessor()
        self.percentage_threshold = 20
        self.cost_threshold = 3000
        self.depth = 1
        self.mini_profit = 10
        self.last_top_id = None
        self.server = "30001"
        self.data_name = {}
        self.previous_result = []
        self.data_loaded = False

        self.initUI()
        self.load_data()
        self.load_auction_house_data("auction_house_data.json")  # Load auction house data

        # Start API data fetching after auction house data is loaded
        QTimer.singleShot(0, self.start_refresh)


    def load_auction_house_data(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.data_name = json.load(f)
                self.data_loaded = True
        except (FileNotFoundError, json.JSONDecodeError) as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement de '{filename}': {e}")
            self.data_loaded = True


    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        # Purchase/Sales Tracking Section
        self.create_purchase_section(self.main_layout)

        # API Data Analysis Section
        self.create_api_analysis_section(self.main_layout)

        # Graph Section
        graph_button = QPushButton("Générer Graphe")
        graph_button.clicked.connect(self.generate_graph)
        self.main_layout.addWidget(graph_button)

        self.centralWidget().setLayout(self.main_layout)


    def create_purchase_section(self, layout):
        purchase_grid = QGridLayout()
        name_label = QLabel("Nom de l'item:")
        purchase_grid.addWidget(name_label, 0, 0)
        self.name_entry = QLineEdit()
        purchase_grid.addWidget(self.name_entry, 0, 1)

        bought_label = QLabel("Prix d'achat:")
        purchase_grid.addWidget(bought_label, 1, 0)
        self.bought_entry = QLineEdit()
        purchase_grid.addWidget(self.bought_entry, 1, 1)

        add_button = QPushButton("Ajouter")
        add_button.clicked.connect(self.add_item)
        purchase_grid.addWidget(add_button, 2, 0, 1, 2)

        self.purchase_tree = QTreeWidget()
        self.purchase_tree.setHeaderLabels(["Nom", "Achat", "Vente", "Timestamp"])
        self.purchase_tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.purchase_tree.itemDoubleClicked.connect(self.edit_item)
        purchase_grid.addWidget(self.purchase_tree, 3, 0, 1, 2)

        calc_button = QPushButton("Calculer totaux")
        calc_button.clicked.connect(self.calculate_totals)
        purchase_grid.addWidget(calc_button, 4, 0, 1, 2)

        self.total_label = QLabel("")
        purchase_grid.addWidget(self.total_label, 5, 0, 1, 2)

        delete_button = QPushButton("Supprimer")
        delete_button.clicked.connect(self.delete_item)
        purchase_grid.addWidget(delete_button, 6, 0, 1, 2)

        layout.addLayout(purchase_grid)


    def create_api_analysis_section(self, layout):
        analysis_grid = QGridLayout()
        analysis_grid.addWidget(QLabel("Profit minimum"), 0, 0)
        self.profit_edit = QLineEdit(str(self.mini_profit))
        self.profit_edit.textChanged.connect(self.update_thresholds)
        analysis_grid.addWidget(self.profit_edit, 0, 1)

        analysis_grid.addWidget(QLabel("Seuil de Coût"), 1, 0)
        self.cost_edit = QLineEdit(str(self.cost_threshold))
        self.cost_edit.textChanged.connect(self.update_thresholds)
        analysis_grid.addWidget(self.cost_edit, 1, 1)

        analysis_grid.addWidget(QLabel("Profondeur"), 2, 0)
        self.depth_edit = QLineEdit(str(self.depth))
        self.depth_edit.textChanged.connect(self.update_thresholds)
        analysis_grid.addWidget(self.depth_edit, 2, 1)

        self.latency_label = QLabel("Latence: ")
        analysis_grid.addWidget(self.latency_label, 3, 0, 1, 2)

        self.api_tree = QTreeWidget()
        self.api_tree.setHeaderLabels(
            ["Name", "Trait", "Depth", "Cost", "Instant Profit", "Profitability (%)", "Item Price", "Occurrences",
             "Sale Price"])
        self.api_tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.api_tree.itemClicked.connect(self.on_item_clicked)
        analysis_grid.addWidget(self.api_tree, 4, 0, 1, 2)

        layout.addLayout(analysis_grid)

    def add_item(self):
        name = self.name_entry.text()
        bought_text = self.bought_entry.text().strip()

        if not bought_text:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer un prix d'achat.")
            return

        try:
            bought = float(bought_text)
            if bought < 0:
                raise ValueError("Le prix d'achat ne peut pas être négatif")
            sold = 0
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            item = Item(name, bought, sold, timestamp)
            self.items.append(item)
            self.update_purchase_tree()
            self.name_entry.clear()
            self.bought_entry.clear()
            self.save_data()
        except ValueError as e:
            QMessageBox.warning(self, "Erreur", f"Erreur de format du prix d'achat: {e}")

    def update_purchase_tree(self):
        self.purchase_tree.clear()
        for item in self.items:
            item_widget = QTreeWidgetItem([item.name, str(item.bought), str(item.sold), item.timestamp])
            self.purchase_tree.addTopLevelItem(item_widget)

    def save_data(self):
        try:
            with open(self.filename, "wb") as f:
                pickle.dump(self.items, f)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde : {e}")

    def load_data(self):
        try:
            with open(self.filename, "rb") as f:
                self.items = pickle.load(f)
                self.update_purchase_tree()
        except (FileNotFoundError, EOFError, pickle.UnpicklingError) as e:
            print(f"Erreur lors du chargement : {e}")

    def edit_item(self, item, column):
        item_index = self.purchase_tree.indexOfTopLevelItem(item)
        item_data = self.items[item_index]
        new_sold, ok = QInputDialog.getDouble(self, "Modifier le prix de vente",
                                             f"Prix de vente pour {item_data.name}:",
                                             item_data.sold, 0, MAX_PRICE, 2)
        if ok:
            item_data.sold = new_sold
            self.update_purchase_tree()
            self.save_data()

    def calculate_totals(self):
        total_spent = sum(item.bought for item in self.items)
        total_earned = sum(item.sold for item in self.items)
        total_profit = total_earned - total_spent
        self.total_label.setText(
            f"Dépenses totales: {total_spent:.2f}  Gains totaux: {total_earned:.2f}  Bénéfice total: {total_profit:.2f}")

    def delete_item(self):
        try:
            selected_item = self.purchase_tree.selectedItems()[0]
            item_index = self.purchase_tree.indexOfTopLevelItem(selected_item)
            del self.items[item_index]
            self.update_purchase_tree()
            self.save_data()
        except IndexError:
            QMessageBox.warning(self, "Erreur", "Aucun élément sélectionné pour la suppression.")


    def start_refresh(self):
        if self.data_loaded:
            self.fetcher = DataFetcher(self.server)
            self.fetcher.data_ready.connect(self.update_api_gui)
            self.fetcher.start()
            self.timer = QTimer()
            self.timer.timeout.connect(self.start_refresh)
            self.timer.start(500)  # Refresh every 60 seconds (adjust as needed)
        else:
            QTimer.singleShot(100, self.start_refresh)

    def process_api_data(self, data, latency):
        if not data:  #More robust handling of empty/None data.
            self.latency_label.setText(f"Latence: Erreur lors de la récupération des données")
            return

        self.latency_label.setText(f"Latence: {latency:.4f} secondes")

        if self.data_name and self.data_name.get('items') and self.data_name.get('traits'):
            results = self.data_processor.process_data(data, self.data_name, self.percentage_threshold,
                                                       self.cost_threshold, self.depth, self.mini_profit)
            self.update_api_tree(results)
        else:
            QMessageBox.critical(self, "Erreur", "Erreur: Impossible de traiter les données API.")


    def update_api_tree(self, results):
        self.api_tree.clear()
        if results:
            for result in results:
                item = QTreeWidgetItem(self.api_tree)
                item.setText(0, result['Name'])
                item.setText(1, result['Trait'])
                item.setText(2, str(result['Depth']))
                item.setText(3, str(result['Cost']))
                item.setText(4, str(result['Instant Profit']))
                item.setText(5, str(result['Profitability (%)']))
                item.setText(6, str(result['Item Price']))
                item.setText(7, str(result['Occurrences']))
                item.setText(8, str(result['Sale Price']))
                min_profit = min(result['Instant Profit'], 1000)
                color = self.get_color(min_profit)
                for i in range(self.api_tree.columnCount()):
                    item.setBackground(i, color)
        else:
            QMessageBox.information(self, "Information", "Aucun résultat trouvé")



    def update_api_gui(self, data, latency):  # Runs in the main thread
        if not data:
            self.latency_label.setText(f"Latence: Erreur lors de la récupération des données")
            return

        self.latency_label.setText(f"Latence: {latency:.4f} secondes")

        if self.data_name and self.data_name.get('items') and self.data_name.get('traits'):
            results = self.data_processor.process_data(data, self.data_name, self.percentage_threshold,
                                                       self.cost_threshold, self.depth, self.mini_profit)
            self.update_api_tree(results)
        else:
            QMessageBox.critical(self, "Erreur", "Erreur: Impossible de traiter les données API.")


        def process_and_update_tree():
            if self.data_name and self.data_name.get('items') and self.data_name.get('traits'):
                results = self.data_processor.process_data(data, self.data_name, self.percentage_threshold,
                                                           self.cost_threshold, self.depth, self.mini_profit)
                if results:
                    self.api_tree.clear()
                    for result in results:
                        item = QTreeWidgetItem(self.api_tree)
                        item.setText(0, result['Name'])
                        item.setText(1, result['Trait'])
                        item.setText(2, str(result['Depth']))
                        item.setText(3, str(result['Cost']))
                        item.setText(4, str(result['Instant Profit']))
                        item.setText(5, str(result['Profitability (%)']))
                        item.setText(6, str(result['Item Price']))
                        item.setText(7, str(result['Occurrences']))
                        item.setText(8, str(result['Sale Price']))
                        min_profit = min(result['Instant Profit'], 1000)
                        color = self.get_color(min_profit)
                        for i in range(self.api_tree.columnCount()):
                            item.setBackground(i, color)
                else:
                    QMessageBox.information(self,"Information","Aucun résultat trouvé")
            else:
                QMessageBox.critical(self, "Erreur", "Erreur: Impossible de traiter les données API.")

        threading.Thread(target=process_and_update_tree).start()

    def generate_graph(self):
        dates = []
        profits = []
        for item in self.items:
            try:
                date_obj = datetime.datetime.strptime(item.timestamp, "%Y-%m-%d %H:%M:%S")
                dates.append(date_obj)
                profit = item.sold - item.bought if item.sold else 0
                profits.append(profit)
            except ValueError as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de l'analyse de la date pour {item.name}: {e}")
                return

        if not dates:
            QMessageBox.warning(self, "Erreur", "Aucune donnée à afficher pour générer le graphique.")
            return

        fig, axes = plt.subplots(1, 2, figsize=(12, 6))

        axes[0].plot(dates, profits, marker='o', linestyle='-', label='Profit par Transaction')
        axes[0].set_xlabel("Date")
        axes[0].set_ylabel("Bénéfice")
        axes[0].set_title("Bénéfices par Transaction")
        axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        axes[0].legend()

        cumulative_profit = [sum(profits[:i+1]) for i in range(len(profits))]
        axes[1].plot(dates, cumulative_profit, marker='o', linestyle='-', label='Profit Cumulé')
        axes[1].set_xlabel("Date")
        axes[1].set_ylabel("Bénéfice Cumulé")
        axes[1].set_title("Bénéfice Cumulé")
        axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        axes[1].legend()
        fig.autofmt_xdate()
        plt.tight_layout()

        canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(canvas, self)

        graph_widget = QWidget()
        graph_layout = QVBoxLayout(graph_widget)
        graph_layout.addWidget(canvas)
        graph_layout.addWidget(toolbar)

        if self.main_layout.count() > 2:
            self.main_layout.itemAt(2).widget().deleteLater()

        self.main_layout.addWidget(graph_widget)
        self.centralWidget().setLayout(self.main_layout)


    def update_thresholds(self):
        try:
            self.mini_profit = int(self.profit_edit.text())
            self.cost_threshold = int(self.cost_edit.text())
            self.depth = int(self.depth_edit.text())
        except ValueError:
            pass

    def on_item_clicked(self, item, column):
        if column == 0:
            name = item.text(0)
            QApplication.clipboard().setText(name)

    def get_color(self, min_profit):
        min_profit = min(min_profit, 1000)
        if min_profit <= 100:
            normalized_p = min_profit / 100.0
            r = int(50 + (255 - 50) * normalized_p)
            g = 255
            b = 50
        else:
            normalized_p = (min_profit - 100) / 900.0
            r = 255
            g = int(255 - (255 - 50) * normalized_p)
            b = 50
        return QColor(r, g, b)


    def load_data(self):
        try:
            with open(self.filename, "rb") as f:
                self.items = pickle.load(f)
                self.update_purchase_tree()
        except (FileNotFoundError, EOFError, pickle.UnpicklingError):
            pass  # Ignore errors on loading


    def update_purchase_tree(self):
        self.purchase_tree.clear()
        for item in self.items:
            item_widget = QTreeWidgetItem([item.name, str(item.bought), str(item.sold), item.timestamp])
            self.purchase_tree.addTopLevelItem(item_widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(1000, 800)
    window.show()
    sys.exit(app.exec_())