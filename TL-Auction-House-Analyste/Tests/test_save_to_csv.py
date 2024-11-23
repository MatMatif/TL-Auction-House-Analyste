import os
import csv
import pytest

def clean_text(text):
    cleaned_text = text.replace("→", "")
    return cleaned_text

def save_to_csv(data, filename="extracted_data.csv"):
    headers = ["Name", "Trait", "Price", "Quantity"]

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

        for item in data:
            for row in item:
                if isinstance(row, dict):
                    row["Name"] = clean_text(row.get("Name", ""))
                    row["Trait"] = clean_text(row.get("Trait", ""))
                    row["Price"] = clean_text(str(row.get("Price", "")))
                    row["Quantity"] = clean_text(str(row.get("Quantity", "")))
                    writer.writerow(row)
                else:
                    print(f"Skipping invalid row: {row}")

    print(f"Les données ont été sauvegardées dans le fichier {filename}")


@pytest.fixture
def sample_data():
    """Fixture pour fournir des données de test"""
    return [
        [{"Name": "Item 1", "Trait": "Trait 1", "Price": "10.99", "Quantity": "5"}],
        [{"Name": "Item 2", "Trait": "Trait 2", "Price": "20.50", "Quantity": "10"}],
        [{"Name": "Item 3", "Trait": "Trait 3", "Price": "15.75", "Quantity": "8"}]
    ]

def test_save_to_csv(sample_data):
    filename = "test_extracted_data.csv"
    save_to_csv(sample_data, filename)

    assert os.path.exists(filename), f"Le fichier {filename} n'a pas été créé"

    with open(filename, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

        assert len(rows) == 3, f"Échec : {len(rows)} lignes trouvées, attendu 3"
        assert set(rows[0].keys()) == {"Name", "Trait", "Price", "Quantity"}, f"Échec : colonnes incorrectes"

        assert rows[0]["Name"] == "Item 1"
        assert rows[0]["Trait"] == "Trait 1"
        assert rows[0]["Price"] == "10.99"
        assert rows[0]["Quantity"] == "5"

    os.remove(filename)

def test_save_to_csv_with_missing_quantity(sample_data):
    data_missing_quantity = [
        [{"Name": "Item 1", "Trait": "Trait 1", "Price": "10.99"}],
        [{"Name": "Item 2", "Trait": "Trait 2", "Price": "20.50"}]
    ]
    
    filename = "test_extracted_data_missing_quantity.csv"
    save_to_csv(data_missing_quantity, filename)

    assert os.path.exists(filename), f"Le fichier {filename} n'a pas été créé"

    with open(filename, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

        assert set(rows[0].keys()) == {"Name", "Trait", "Price", "Quantity"}, f"Échec : colonnes incorrectes"
        assert rows[0]["Quantity"] == "", f"Échec : la quantité est manquante"

    os.remove(filename)
