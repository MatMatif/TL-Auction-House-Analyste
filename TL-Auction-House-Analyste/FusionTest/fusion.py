from dataclasses import dataclass
import pickle
import sys
import datetime
from typing import Optional
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout,
                             QGridLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QHeaderView, QMessageBox, QInputDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QColor

MAX_PRICE = 999999999

@dataclass
class Item:
    name: str
    bought: float
    sold: Optional[float] = 0.0
    timestamp: str = ""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Log des Achats")
        self.filename = "achat_data.pickle"
        self.items = []
        self.initUI()
        self.load_data()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)  # Create a main vertical layout
        grid = QGridLayout()

        # Input fields (Removed the duplicate block)
        name_label = QLabel("Nom de l'item:")
        grid.addWidget(name_label, 0, 0)
        self.name_entry = QLineEdit()
        grid.addWidget(self.name_entry, 0, 1)

        bought_label = QLabel("Prix d'achat:")
        grid.addWidget(bought_label, 1, 0)
        self.bought_entry = QLineEdit()
        grid.addWidget(self.bought_entry, 1, 1)

        add_button = QPushButton("Ajouter")
        add_button.clicked.connect(self.add_item)
        grid.addWidget(add_button, 2, 0, 1, 2)

        # Tree Widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Nom", "Achat", "Vente", "Timestamp"])
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tree.itemDoubleClicked.connect(self.edit_item)
        grid.addWidget(self.tree, 3, 0, 1, 2)

        # Buttons
        calc_button = QPushButton("Calculer totaux")
        calc_button.clicked.connect(self.calculate_totals)
        grid.addWidget(calc_button, 4, 0, 1, 2)

        self.total_label = QLabel("")
        grid.addWidget(self.total_label, 5, 0, 1, 2)

        delete_button = QPushButton("Supprimer")
        delete_button.clicked.connect(self.delete_item)
        grid.addWidget(delete_button, 6, 0, 1, 2)

        graph_button = QPushButton("Générer Graphe")
        graph_button.clicked.connect(self.generate_graph)
        grid.addWidget(graph_button, 7, 0, 1, 2)

        self.main_layout.addLayout(grid)
        self.centralWidget().setLayout(self.main_layout)
    
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
            self.update_tree()
            self.name_entry.clear()
            self.bought_entry.clear()
            self.save_data()
        except ValueError as e:
            QMessageBox.warning(self, "Erreur", f"Erreur de format du prix d'achat: {e}")


    def update_tree(self):
        self.tree.clear()
        for item in self.items:
            item_widget = QTreeWidgetItem([item.name, str(item.bought), str(item.sold), item.timestamp])
            self.tree.addTopLevelItem(item_widget)

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
                self.update_tree()
        except (FileNotFoundError, EOFError, pickle.UnpicklingError) as e:
            print(f"Erreur lors du chargement : {e}")  # Log the error;  no need for multiple except blocks

    def edit_item(self, item, column):
        item_index = self.tree.indexOfTopLevelItem(item)
        item_data = self.items[item_index]
        new_sold, ok = QInputDialog.getDouble(self, "Modifier le prix de vente",
                                             f"Prix de vente pour {item_data.name}:",
                                             item_data.sold, 0, MAX_PRICE, 2)
        if ok:
            item_data.sold = new_sold
            self.update_tree()
            self.save_data()


    def calculate_totals(self):
        total_spent = sum(item.bought for item in self.items)
        total_earned = sum(item.sold for item in self.items)
        total_profit = total_earned - total_spent
        self.total_label.setText(f"Dépenses totales: {total_spent:.2f}  Gains totaux: {total_earned:.2f}  Bénéfice total: {total_profit:.2f}")

    def delete_item(self):
        try:
            selected_item = self.tree.selectedItems()[0]
            item_index = self.tree.indexOfTopLevelItem(selected_item)
            del self.items[item_index]
            self.update_tree()
            self.save_data()
        except IndexError:
            QMessageBox.warning(self, "Erreur", "Aucun élément sélectionné pour la suppression.")

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

        # Matplotlib canvas and toolbar integration in PyQt
        canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(canvas, self)

        graph_widget = QWidget()
        graph_layout = QVBoxLayout(graph_widget)
        graph_layout.addWidget(canvas)
        graph_layout.addWidget(toolbar)

        if self.main_layout.count() > 1:
            self.main_layout.itemAt(1).widget().deleteLater()

        self.main_layout.addWidget(graph_widget)
        self.centralWidget().setLayout(self.main_layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())