from bs4 import BeautifulSoup
import pytest
import re

def clean_and_convert_to_number(value):
    try:
        value = value.strip()
        if "," in value:
            value = value.replace(",", "")
        number = float(value)
        if number.is_integer():
            return int(number)
        return number
    except ValueError:
        return 0

def clean_string(s):
    if s:
        return re.sub(r'\s+', ' ', s.strip().replace("\n", " ").replace("\t", " ").replace("\r", ""))
    return s

def parse_table_html(table_html):
    """Parse le HTML de la table et retourne les données extraites"""
    extracted_data = []
    
    if table_html:
        soup = BeautifulSoup(table_html, "html.parser")
        tbody = soup.find("tbody")
        
        if tbody:
            for row in tbody.find_all("tr"):
                try:
                    name = clean_string(row.find_all("td")[2].get_text(strip=True))
                    quantity = clean_string(row.find_all("td")[3].get_text(strip=True))
                    price = clean_string(row.find_all("td")[4].get_text(strip=True))

                    if name and quantity and price:
                        price_int = clean_and_convert_to_number(price)
                        quantity_int = clean_and_convert_to_number(quantity)
                        extracted_data.append({
                            "Name": name,
                            "Trait": "NONE",
                            "Quantity": quantity_int,
                            "Price": price_int
                        })
                except IndexError:
                    continue
    
    return extracted_data

@pytest.fixture # Fixture pour du contenu HTML simulé
def valid_html():
    return """
    <table>
        <tbody>
            <tr>
                <td>1</td>
                <td>Item 1</td>
                <td>Name 1</td>
                <td>10</td>
                <td>0.500</td>
            </tr>
            <tr>
                <td>2</td>
                <td>Item 2</td>
                <td>Name 2</td>
                <td>1</td>
                <td>2,000.51</td>
            </tr>
        </tbody>
    </table>
    """

@pytest.fixture # Fixture pour récupérer le contenu HTML depuis un fichier
def html_from_file():
    with open("details_page_no_trait_sample.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    return html_content

@pytest.fixture # Fixture avec un contenu HTML vide
def empty_html():
    return "<html><body>No data</body></html>"

@pytest.fixture # Fixture de données invalides
def invalid_structure(): 
    return """
    <table>
        <tbody>
            <tr>
                <td>1</td>
                <td>Item 1</td>
            </tr>
        </tbody>
    </table>
    """

@pytest.fixture # Ficture de données incorectes
def incorrect_data():
    return """
    <table>
        <tbody>
            <tr>
                <td>1</td>
                <td>Item 1</td>
                <td>Name 1</td>
                <td>pipi</td>
                <td>prout</td>
            </tr>
        </tbody>
    </table>
    """

def test_parse_table_html_valid(valid_html): # Cas de données valides
    expected_data = [
        {"Name": "Name 1", "Trait": "NONE", "Quantity": 10, "Price": 0.5},
        {"Name": "Name 2", "Trait": "NONE", "Quantity": 1, "Price": 2000.51}
    ]
    
    result = parse_table_html(valid_html)
    assert result == expected_data, f"Échec: {result} != {expected_data}"

def test_parse_table_html_from_file(html_from_file):  # Cas avec HTML lu depuis le fichier
    expected_data = [
        {"Name": "Quality Marind", "Trait": "NONE", "Quantity": 1000, "Price": 0.047},
        {"Name": "Quality Marind", "Trait": "NONE", "Quantity": 1000, "Price": 0.047},
        {"Name": "Quality Marind", "Trait": "NONE", "Quantity": 1000, "Price": 0.047},
        {"Name": "Quality Marind", "Trait": "NONE", "Quantity": 1000, "Price": 0.047},
        {"Name": "Quality Marind", "Trait": "NONE", "Quantity": 1000, "Price": 0.047},
        {"Name": "Quality Marind", "Trait": "NONE", "Quantity": 1000, "Price": 0.047},
        {"Name": "Quality Marind", "Trait": "NONE", "Quantity": 1000, "Price": 0.047},
        {"Name": "Quality Marind", "Trait": "NONE", "Quantity": 1000, "Price": 0.047},
        {"Name": "Quality Marind", "Trait": "NONE", "Quantity": 1000, "Price": 0.047},
        {"Name": "Quality Marind", "Trait": "NONE", "Quantity": 1000, "Price": 0.047}
    ]
    
    result = parse_table_html(html_from_file)
    assert result == expected_data, f"Échec: {result} != {expected_data}"

def test_parse_table_html_empty(empty_html): # Cas où il n'y a pas de données à extraire
    result = parse_table_html(empty_html)
    assert result == [], f"Échec: {result} != []"

def test_parse_table_html_invalid_structure(invalid_structure): # Cas ou la structure HTML est invalide
    result = parse_table_html(invalid_structure)
    assert result == [], f"Échec: {result} != []"

def test_parse_table_html_incorrect_data(incorrect_data): # Cas ou les données sont incorrectes dans la colonne de quantité
    result = parse_table_html(incorrect_data)
    assert result == [{"Name": "Name 1", "Trait": "NONE", "Quantity": 0, "Price": 0}], f"Échec: {result}"


