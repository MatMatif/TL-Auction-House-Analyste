import pytest
from bs4 import BeautifulSoup

def check_trait_column_in_html(table_html):
    if table_html:
        soup = BeautifulSoup(table_html, "html.parser")
        thead = soup.find("thead")
        
        if thead:
            for th in thead.find_all("th"):
                if 'Trait' in th.get_text(strip=True):
                    return True
    return False

@pytest.fixture # Fixture pour une table avec la colonne 'Trait'
def table_with_trait():
    return """
    <table>
        <thead>
            <tr>
                <th>Nom</th>
                <th>Âge</th>
                <th>Trait</th>
                <th>Ville</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>caca</td>
                <td>pipi</td>
                <td>prout</td>
                <td>double_prout</td>
            </tr>
        </tbody>
    </table>
    """

@pytest.fixture # Fixture pour une table sans la colonne 'Trait'
def table_without_trait():
    return """
    <table>
        <thead>
            <tr>
                <th>Nom</th>
                <th>Âge</th>
                <th>Ville</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Alice</td>
                <td>30</td>
                <td>Paris</td>
            </tr>
        </tbody>
    </table>
    """

@pytest.fixture # Fixture pour une table vide
def empty_table():
    return """
    <table>
        <thead>
            <tr></tr>
        </thead>
        <tbody></tbody>
    </table>
    """

@pytest.fixture # Fixture pour une table sans thead
def no_thead_table():
    return """
    <table>
        <tbody>
            <tr>
                <td>Nom</td>
                <td>Âge</td>
                <td>Trait</td>
            </tr>
        </tbody>
    </table>
    """

@pytest.fixture # Fixture pour récupérer le contenu HTML depuis un fichier 
def html_from_file_trait():
    with open("details_page_trait_sample.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    return html_content

@pytest.fixture # Fixture pour récupérer le contenu HTML depuis un fichier
def html_from_file_no_trait():
    with open("details_page_no_trait_sample.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    return html_content

def test_column_trait_exists(table_with_trait): # Cas ou la colonne 'Trait' existe dans la table
    assert check_trait_column_in_html(table_with_trait) == True

def test_column_trait_not_exists(table_without_trait): # Cas ou la colonne 'Trait' n'existe pas dans la table
    assert check_trait_column_in_html(table_without_trait) == False

def test_empty_table(empty_table): # Cas ou la table est vide
    assert check_trait_column_in_html(empty_table) == False

def test_no_thead(no_thead_table): # Cas ou la table n'a pas de thead
    assert check_trait_column_in_html(no_thead_table) == False

def test_no_thead_with_file_trait(html_from_file_trait): # Cas ou la table n'a pas de thead
    assert check_trait_column_in_html(html_from_file_trait) == True

def test_no_thead_with_file_no_trait(html_from_file_no_trait): # Cas ou la table n'a pas de thead
    assert check_trait_column_in_html(html_from_file_no_trait) == False
