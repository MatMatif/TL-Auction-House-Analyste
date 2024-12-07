import pickle
import tkinter as tk
from tkinter import ttk
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Item:
    def __init__(self, name, bought, sold, timestamp):
        self.name = name
        self.bought = bought
        self.sold = sold
        self.timestamp = timestamp  # Add timestamp attribute


    def __str__(self):
        return f"Item(name='{self.name}', bought={self.bought}, sold={self.sold}, timestamp={self.timestamp})"

class App:
    def __init__(self, master):
        self.master = master
        master.title("Log des Achats")
        self.filename = "achat_data.pickle"
        self.items = []


        # Labels and entry fields (unchanged)
        self.name_label = ttk.Label(master, text="Nom de l'item:")
        self.name_label.grid(row=0, column=0, sticky="w")
        self.name_entry = ttk.Entry(master)
        self.name_entry.grid(row=0, column=1)

        self.bought_label = ttk.Label(master, text="Prix d'achat:")
        self.bought_label.grid(row=1, column=0, sticky="w")
        self.bought_entry = ttk.Entry(master)
        self.bought_entry.grid(row=1, column=1)

        self.add_button = ttk.Button(master, text="Ajouter", command=self.add_item)
        self.add_button.grid(row=2, column=0, columnspan=2)

        # Create the Treeview widget HERE
        self.tree = ttk.Treeview(master, columns=("Nom", "Achat", "Vente"), show="headings")
        self.tree.heading("Nom", text="Nom")
        self.tree.heading("Achat", text="Achat")
        self.tree.heading("Vente", text="Vente")
        self.tree.grid(row=3, column=0, columnspan=2, sticky="nsew")
        self.tree.bind("<Double-1>", self.edit_item)

        # Set minimum column widths (Solution 1)
        self.tree.column("Nom", minwidth=100, stretch=tk.YES)
        self.tree.column("Achat", minwidth=80, stretch=tk.YES)
        self.tree.column("Vente", minwidth=80, stretch=tk.YES)


        # Buttons (unchanged)
        self.calc_button = ttk.Button(master, text="Calculer totaux", command=self.calculate_totals)
        self.calc_button.grid(row=4, column=0, columnspan=2)

        self.total_label = ttk.Label(master, text="")
        self.total_label.grid(row=5, column=0, columnspan=2)

        self.delete_button = ttk.Button(master, text="Supprimer", command=self.delete_item)
        self.delete_button.grid(row=6, column=0, columnspan=2)

        self.graph_button = ttk.Button(master, text="Générer Graphe", command=self.generate_graph)
        self.graph_button.grid(row=7, column=0, columnspan=2)

        self.load_data() # Call load_data AFTER tree is created

    def add_item(self):
        name = self.name_entry.get()
        try:
            bought = float(self.bought_entry.get())
            sold = 0
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Get current timestamp
            item = Item(name, bought, sold, timestamp) # Pass timestamp to Item constructor
            self.items.append(item)
            self.update_tree()
            self.name_entry.delete(0, tk.END)
            self.bought_entry.delete(0, tk.END)
            self.save_data()
        except ValueError:
            print("Valeur invalide. Veuillez entrer des nombres.")

    def update_tree(self):
        self.tree.delete(*self.tree.get_children())
        for item in self.items:
            self.tree.insert("", tk.END, values=(item.name, item.bought, item.sold, item.timestamp)) # Add timestamp to values

    def save_data(self):
      try:
          with open(self.filename, "wb") as f:
              pickle.dump(self.items, f)
              print("Données sauvegardées avec succès.")
      except Exception as e:
          print(f"Erreur lors de la sauvegarde : {e}")

    def load_data(self):
        try:
            with open(self.filename, "rb") as f:
                self.items = pickle.load(f)
                print("Données chargées :", self.items)
                self.update_tree()
        except FileNotFoundError:
            print("Aucun fichier de données trouvé. Initialisation d'une nouvelle liste.")
            self.items = []
        except EOFError:
            print("Fichier de données vide. Initialisation d'une nouvelle liste.")
            self.items = []
        except pickle.UnpicklingError as e:
            print(f"Erreur lors du dé-serialisation Pickle: {e}. Initialisation d'une nouvelle liste.")
            self.items = []
        except Exception as e:
            print(f"Erreur inattendue lors du chargement : {e}. Initialisation d'une nouvelle liste.")
            import traceback
            traceback.print_exc()
            self.items = []

    def edit_item(self, event):
        item_id = self.tree.selection()[0]
        item_index = self.tree.index(item_id)
        item = self.items[item_index]

        # Crée une fenêtre pop-up pour éditer le prix de vente
        edit_window = tk.Toplevel(self.master)
        edit_window.title("Modifier le prix de vente")

        ttk.Label(edit_window, text=f"Prix de vente pour {item.name}:").grid(row=0, column=0)
        new_sold_entry = ttk.Entry(edit_window)
        new_sold_entry.grid(row=0, column=1)

        def save_changes():
            try:
                item.sold = float(new_sold_entry.get())
                self.update_tree()
                self.save_data()  # Sauvegarde après modification
                edit_window.destroy()  # Ferme la fenêtre pop-up
            except ValueError:
                print("Veuillez entrer un nombre valide pour le prix de vente.")

        ttk.Button(edit_window, text="Enregistrer", command=save_changes).grid(row=1, column=0, columnspan=2)

    def calculate_totals(self):
        spend = sum(item.bought for item in self.items)
        earned = sum(item.sold for item in self.items)
        benef = earned - spend
        self.total_label.config(text=f"Dépenses: {spend:.2f}  Gains: {earned:.2f}  Bénéfice: {benef:.2f}")

    def delete_item(self):
        try:
            selected_item = self.tree.selection()[0]
            item_index = self.tree.index(selected_item)
            del self.items[item_index]
            self.update_tree()
            self.save_data()  # Sauvegarde après suppression
        except IndexError:
            print("Aucun élément sélectionné pour la suppression.")

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
                print(f"Error parsing timestamp for item {item.name}: {e}")

        if not dates:
            print("No data to plot.")
            return

        fig, axes = plt.subplots(1, 2, figsize=(12, 6)) # 1 row, 2 columns

        # First subplot: Individual Profits
        axes[0].plot(dates, profits, marker='o', linestyle='-')
        axes[0].set_xlabel("Date")
        axes[0].set_ylabel("Bénéfice")
        axes[0].set_title("Bénéfices par Transaction")
        axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        fig.autofmt_xdate()

        # Second subplot: Cumulative Profit
        cumulative_profit = [sum(profits[:i+1]) for i in range(len(profits))]
        axes[1].plot(dates, cumulative_profit, marker='o', linestyle='-')
        axes[1].set_xlabel("Date")
        axes[1].set_ylabel("Bénéfice Cumulé")
        axes[1].set_title("Bénéfice Cumulé")
        axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        fig.autofmt_xdate()

        # Adjust layout to prevent overlapping
        plt.tight_layout() #This helps prevent overlapping of titles and labels

        canvas = FigureCanvasTkAgg(fig, master=self.master)
        canvas.draw()
        canvas.get_tk_widget().grid(row=8, column=0, columnspan=2)




# Lancement de l'application
root = tk.Tk()
app = App(root)
root.mainloop()
