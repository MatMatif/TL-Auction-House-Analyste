# Analyse de l'Auction House - Throne and Liberty

Ce projet utilise Selenium et BeautifulSoup pour extraire et analyser les données de l'**Auction House** du jeu vidéo **Throne and Liberty**. L'objectif est d'extraire des informations telles que les noms des objets, leurs traits et les prix, puis de les sauvegarder dans un fichier Excel pour une analyse plus poussée.

## Fonctionnement

### Prérequis

Avant de lancer le programme, assurez-vous que les éléments suivants sont installés sur votre machine :

- **Python 3.x** (Téléchargez-le depuis [python.org](https://www.python.org/))
- **Selenium** : Utilisé pour automatiser l'interaction avec la page web.
- **BeautifulSoup** : Pour analyser et nettoyer le HTML extrait.
- **Pandas** : Pour manipuler et sauvegarder les données dans un fichier Excel.
- **ChromeDriver** : Pilote pour Selenium (assurez-vous qu'il est compatible avec votre version de Chrome/Brave).

Vous pouvez installer les bibliothèques Python requises avec la commande suivante :

```bash
pip install selenium beautifulsoup4 pandas
```

## Structure du projet

- **main.py** : Le script principal qui effectue l'extraction des données et les sauvegarde dans un fichier Excel.
- **chromedriver.exe** : Le fichier du pilote Selenium pour Chrome/Brave.
- **README.md** : Ce fichier, qui explique le fonctionnement du projet.

## Explication du processus

1. **Accès à la page** : Le programme commence par accéder à la page de l'Auction House de **Throne and Liberty**.
2. **Navigation** : Il sélectionne les filtres nécessaires, tels que "All" et "Europe", pour affiner la recherche.
3. **Extraction des données** : Le programme collecte les informations des différentes entrées de l'Auction House, y compris le nom de l'objet, son trait et son prix.
4. **Sauvegarde dans Excel** : Une fois les données extraites et nettoyées, elles sont sauvegardées dans des fichiers Excel pour faciliter leur analyse.
5. **Automatisation** : Tout le processus est automatisé via Selenium pour éviter les tâches manuelles répétitives.

## Détails du code

Le programme utilise **Selenium** pour automatiser le navigateur Brave, et **BeautifulSoup** pour analyser le HTML brut et extraire les données pertinentes.

- Le script commence par initialiser un navigateur Brave en mode **headless** pour exécuter les actions sans interface graphique.
- Il interagit avec des menus déroulants pour filtrer les résultats, puis itère sur les lignes du tableau d'objets pour extraire les données.
- Les données extraites sont nettoyées en supprimant les balises inutiles et sont enregistrées dans un fichier Excel via **Pandas**.

## Exemple de données extraites

Les données extraites contiennent des informations sur les objets de l'Auction House, telles que :

- **Name** : Le nom de l'objet
- **Trait** : Le trait de l'objet
- **Price** : Le prix de l'objet

Les données sont sauvegardées dans un fichier Excel sous la forme d'un tableau structuré.

### Exemple de fichier Excel

| Name           | Trait       | Price   |
|----------------|-------------|---------|
| Sword of Fire  | Fire        | 1000    |
| Shield of Ice  | Ice         | 500     |
| Potion of Speed| Speed       | 200     |

## Limitations

- Le script est actuellement configuré pour extraire uniquement les 10 premières entrées de l'Auction House. Vous pouvez ajuster cette limite en modifiant le paramètre dans la boucle d'itération.
- Le programme repose sur des sélecteurs CSS qui peuvent changer si la structure du site web est modifiée.
