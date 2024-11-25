// Importation des dépendances
import * as devalue from 'devalue';
import { decompress } from 'compress-json';
import fs from 'fs';  // Importation de fs pour écrire dans un fichier

// Exemple d'utilisation de l'API : Fetch de données depuis l'API d'enchères
async function fetchAuctionHouseData() {
  try {
    // Récupérer les données de l'API
    const apiResp = await fetch('https://tldb.info/auction-house/__data.json').then(r => r.json());

    // Extraire les données utiles avec devalue
    const apiData = devalue.unflatten(apiResp.nodes.find((e) => e?.type === 'data').data);

    // Décompresser les éléments de l'enchère
    const items = decompress(apiData.items);
    const traits = apiData.traits;

    // Créer un objet avec les données à sauvegarder
    const dataToSave = {
      items: items,
      traits: traits
    };

    // Sauvegarder les données dans un fichier JSON
    fs.writeFileSync('auction_house_data.json', JSON.stringify(dataToSave, null, 2));
    console.log('Données des enchères sauvegardées dans "auction_house_data.json"');
  } catch (error) {
    console.error('Erreur lors de la récupération des données de l\'API:', error);
  }
}

// Exemple d'utilisation de l'API : Récupération des prix des objets
async function fetchItemPrices() {
  try {
    // Récupérer les prix des objets depuis l'API
    const apiData = await fetch('https://tldb.info/api/ah/prices').then(r => r.json());

    let { list, total, regions } = apiData;

    // Décompresser les prix par serveur
    Object.keys(list).forEach((server) => {
      list[server] = decompress(JSON.parse(list[server]));
    });

    // Créer un objet avec les données des prix à sauvegarder
    const dataToSave = {
      list: list,
      total: total,
      regions: regions
    };

    // Sauvegarder les données dans un fichier JSON
    fs.writeFileSync('item_prices_data.json', JSON.stringify(dataToSave, null, 2));
    console.log('Données des prix des objets sauvegardées dans "item_prices_data.json"');

  } catch (error) {
    console.error('Erreur lors de la récupération des prix:', error);
  }
}

// Appels à l'API
//fetchAuctionHouseData();
fetchItemPrices();