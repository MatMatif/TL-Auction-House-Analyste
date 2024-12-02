import json
import os
import requests

with open('data.json', 'r') as file:
    data = json.load(file)

base_url = "https://cdn.tldb.info/db/images/ags/v8/128/"

save_dir = "icons"
os.makedirs(save_dir, exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

def download_image(url, filepath):
    try:
        response = requests.get(url, headers=headers, stream=True)
        
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Telecharge avec succès : {filepath}")
        else:
            print(f"Erreur HTTP {response.status_code} lors du telechargement de {url}")
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors du telechargement de {url}: {e}")

def is_image_downloaded(filename):
    return os.path.exists(filename)

downloaded_files = set()
for item in data["items"]:
    icon_path = item["icon"].lower()
    image_name = icon_path.split('/')[-1]
    full_url = base_url + icon_path + ".png" 
    filepath = os.path.join(save_dir, f"{image_name}.png")
    
    if image_name not in downloaded_files:
        download_image(full_url, filepath)
        downloaded_files.add(image_name)
    else:
        print(f"Image dejà telechargee : {image_name}")

print("Telechargement termine.")
