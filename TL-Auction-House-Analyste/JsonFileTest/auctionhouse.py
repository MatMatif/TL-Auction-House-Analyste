import json
import requests
from compress_json import decompress
import time

# URL de l'API
url = "https://tldb.info/api/ah/prices"

# Configuration des en-têtes HTTP
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}
# Mesure du temps pour récupérer les données
start_header_time = time.time()
response = requests.get(url, headers=headers)
end_header_time = time.time()

# Vérification du statut de la réponse
if response.status_code == 200:
    # Charger les données JSON
    data = response.json()

    # Extraction des sous-données
    list_data = data["list"]

    # Mesure du temps pris pour la décompression
    dictionnaire = {}
        
    start_decompress_time = time.time()
    for server in list_data:
        dictionnaire[server] = decompress(json.loads(list_data[server]))
        
    end_decompress_time = time.time()

    # Calcul des durées
    header_time = end_header_time - start_header_time
    decompress_time = end_decompress_time - start_decompress_time

    # Affichage des temps
    print(f"Temps pour récupérer les données (header) : {header_time:.6f} secondes")
    print(f"Temps pour décompresser les données : {decompress_time:.6f} secondes")

    # Écriture des données mises à jour dans un fichier
    with open("data_python.json", "w", encoding="utf-8") as fd:
        fd.write(json.dumps(dictionnaire, ensure_ascii=False, indent=2))
else:
    print(f"Erreur lors de la récupération des données : {response.status_code}")

