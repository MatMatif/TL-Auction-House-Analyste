from bs4 import BeautifulSoup
import pytest
import re

def get_total_entries_from_html(html_content):
    """
    Fonction pour extraire le nombre total d'entrées depuis une chaîne HTML.
    """
    try:
        soup = BeautifulSoup(html_content, "html.parser")

        pagination_element = soup.select_one('aside.dt-pagination-rowcount')
        pagination_text = pagination_element.text.strip() if pagination_element else None
        
        if not pagination_text:
            raise ValueError("Le texte de pagination est introuvable.")

        match = re.search(r'of (\d+) entries', pagination_text)
        if match:
            total_entries = int(match.group(1))
            return total_entries
        else:
            raise ValueError("Impossible d'extraire le nombre total d'entrées depuis le texte.")
    except Exception as e:
        print(f"Erreur lors de l'extraction des entrées : {e}")
        return 0

@pytest.fixture # Fixture pour du contenu HTML simulé
def html_content():
    return """
    <html>
        <body>
            <aside class="dt-pagination-rowcount">
                Showing 1 to 10 of 1294 entries
            </aside>
        </body>
    </html>
    """

@pytest.fixture # Fixture pour du contenu depuis un fichier
def html_content_from_file():
    """Fixture pour charger le fichier HTML depuis 'main_page_sample.html'"""
    with open("main_page_sample.html", "r", encoding="utf-8") as f:
        return f.read()


def test_get_total_entries_from_html(html_content):
    expected_total_entries = 1294
    total_entries = get_total_entries_from_html(html_content)
    assert total_entries == expected_total_entries, f"Échec : attendu {expected_total_entries}, mais obtenu {total_entries}"

def test_get_total_entries_no_pagination(): # HTML sans la section de pagination

    html_content_no_pagination = """
    <html>
        <body>
            <div>Pas de pagination ici</div>
        </body>
    </html>
    """
    total_entries = get_total_entries_from_html(html_content_no_pagination)
    assert total_entries == 0, f"Échec : attendu 0, mais obtenu {total_entries}"

def test_get_total_entries_bad_format(): # HTML avec une pagination mal formée
    html_content_bad_format = """
    <html>
        <body>
            <aside class="dt-pagination-rowcount">
                Showing 1 to 10 of not-a-number entries
            </aside>
        </body>
    </html>
    """
    total_entries = get_total_entries_from_html(html_content_bad_format)
    assert total_entries == 0, f"Échec : attendu 0, mais obtenu {total_entries}"

def test_get_total_entries_large_number(): # HTML avec un nombre très élevé
    html_content_large_number = """
    <html>
        <body>
            <aside class="dt-pagination-rowcount">
                Showing 1 to 10 of 9999999 entries
            </aside>
        </body>
    </html>
    """
    total_entries = get_total_entries_from_html(html_content_large_number)
    expected_total_entries = 9999999
    assert total_entries == expected_total_entries, f"Échec : attendu {expected_total_entries}, mais obtenu {total_entries}"

def test_get_total_entries_from_file(html_content_from_file):
    """Test pour extraire le nombre d'entrées depuis le fichier 'main_page_sample.html'"""
    total_entries = get_total_entries_from_html(html_content_from_file)
    expected_total_entries = 1294
    assert total_entries == expected_total_entries, f"Échec : attendu {expected_total_entries}, mais obtenu {total_entries}"
