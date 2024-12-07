import requests
from compress_json import decompress
import base64
import json
from typing import Any

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}
# Constants simulant les valeurs spéciales
UNDEFINED = -1
NAN = -2
POSITIVE_INFINITY = -3
NEGATIVE_INFINITY = -4
NEGATIVE_ZERO = -5
HOLE = None


def decode64(base64_str: str) -> bytes:
    """Décodage Base64."""
    return base64.b64decode(base64_str)


def unflatten(parsed: Any, revivers=None) -> Any:
    """Reconstitue un objet sérialisé par devalue."""

    if not isinstance(parsed, list) or len(parsed) == 0:
        raise ValueError("Invalid input")

    values = parsed
    hydrated = [None] * len(values)

    def hydrate(index: int, standalone=False):
        if index == UNDEFINED:
            return None
        if index == NAN:
            return float('nan')
        if index == POSITIVE_INFINITY:
            return float('inf')
        if index == NEGATIVE_INFINITY:
            return float('-inf')
        if index == NEGATIVE_ZERO:
            return -0.0

        if standalone:
            raise ValueError("Invalid input")

        if hydrated[index] is not None:
            return hydrated[index]

        value = values[index]

        if not isinstance(value, (dict, list)):
            hydrated[index] = value
        elif isinstance(value, list):
            if isinstance(value[0], str):  # Typed object
                type_ = value[0]
                if revivers and type_ in revivers:
                    hydrated[index] = revivers[type_](hydrate(value[1]))
                else:
                    if type_ == "Date":
                        hydrated[index] = value[1]  # Date handling (if needed)
                    elif type_ == "Set":
                        hydrated[index] = set(hydrate(i) for i in value[1:])
                    elif type_ == "Map":
                        hydrated[index] = {
                            hydrate(value[i]): hydrate(value[i + 1])
                            for i in range(1, len(value), 2)
                        }
                    elif type_ == "RegExp":
                        hydrated[index] = f"RegExp({value[1]}, {value[2]})"  # Mock
                    elif type_ == "Object":
                        hydrated[index] = object(value[1])
                    elif type_ == "BigInt":
                        hydrated[index] = int(value[1])
                    elif type_ == "null":
                        hydrated[index] = {
                            hydrate(value[i]): hydrate(value[i + 1])
                            for i in range(1, len(value), 2)
                        }
                    elif type_ in [
                        "Int8Array",
                        "Uint8Array",
                        "Uint8ClampedArray",
                        "Int16Array",
                        "Uint16Array",
                        "Int32Array",
                        "Uint32Array",
                        "Float32Array",
                        "Float64Array",
                        "BigInt64Array",
                        "BigUint64Array",
                    ]:
                        arraybuffer = decode64(value[1])
                        hydrated[index] = list(arraybuffer)  # Mock TypedArray
                    elif type_ == "ArrayBuffer":
                        hydrated[index] = decode64(value[1])
                    else:
                        raise ValueError(f"Unknown type {type_}")
            else:  # Normal array
                hydrated[index] = [
                    hydrate(v) if v != HOLE else None for v in value
                ]
        else:  # Normal object
            hydrated[index] = {k: hydrate(v) for k, v in value.items()}

        return hydrated[index]

    return hydrate(0)


def fetch_auction_house_prices():
    prices_url = "https://tldb.info/api/ah/prices"
    response = requests.get(prices_url, headers=HEADERS)

    if response.status_code == 200:
        prices_data = response.json()
        server_prices = prices_data.get("list", {})  # Utilise get pour éviter une KeyError si "list" est absent

        decompressed_prices = {}
        for server, compressed_data in server_prices.items():
            try:
                decompressed_prices[server] = decompress(json.loads(compressed_data))
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Erreur lors de la décompression des données du serveur {server}: {e}")

        with open("auction_house_prices.json", "w", encoding="utf-8") as f:
            json.dump(decompressed_prices, f, ensure_ascii=False, indent=2)
    else:
        print(f"Erreur lors de la récupération des prix: {response.status_code}")


def fetch_auction_house_data():
    data_url = "https://tldb.info/auction-house/__data.json"
    response = requests.get(data_url, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        nodes = data.get("nodes", [])

        if not nodes:
            print("La clé 'nodes' est absente ou vide dans les données.")
            return

        data_node = next((node for node in nodes if node and node.get("type") == "data"), None)

        if not data_node:
            print("Aucun nœud avec 'type: data' trouvé.")
            return

        try:
            unflattened_data = unflatten(data_node["data"])
            items = decompress(unflattened_data["items"])
            auction_house_data = {"items": items, "traits": unflattened_data["traits"]}

            with open("auction_house_data.json", "w", encoding="utf-8") as f:
                json.dump(auction_house_data, f, ensure_ascii=False, indent=2)
        except (KeyError, TypeError) as e:
            print(f"Erreur lors du traitement des données: {e}")

    else:
        print(f"Erreur lors de la récupération des données: {response.status_code}")


# Appel de la fonction
fetch_auction_house_data()
fetch_auction_house_prices()
