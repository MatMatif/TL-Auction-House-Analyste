from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)  # Vous pouvez remplacer par 'firefox' ou 'webkit'
    page = browser.new_page()

    # Accéder à la page
    page.goto("https://tldb.info/auction-house")

    # Attendre la présence d'un élément
    page.wait_for_selector("aside.dt-pagination-rowcount")

    # Interaction avec un dropdown
    page.click('.btn.btn-secondary.w-100.fw-semi-bold.dropdown-toggle')
    page.click('button:text("All")')  # Cliquer sur "All"

    # Récupérer le nombre total d'entrées
    pagination_text = page.text_content('aside.dt-pagination-rowcount')
    print(f"Pagination: {pagination_text}")

    # Fermer le navigateur
    browser.close()
