import json
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

URL = "https://www.enforcementtracker.com/"

def get_fines():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # ✅ Navigate to page and wait until network is idle
        page.goto(URL, wait_until="networkidle")

        # ✅ Give JS a moment to hydrate the page content
        page.wait_for_timeout(5000)  # wait 5 seconds explicitly

        # ✅ Wait for the table to appear with extended timeout
        page.wait_for_selector("table#enforcementtable", timeout=90000)

        # ✅ Parse table contents using BeautifulSoup
        soup = BeautifulSoup(page.content(), "html.parser")
        rows = soup.select("table#enforcementtable tbody tr")

        fines = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 5:
                fines.append({
                    "date": cols[0].text.strip(),
                    "company": cols[1].text.strip(),
                    "country": cols[2].text.strip(),
                    "amount": cols[3].text.strip().replace("€", "").replace(",", ""),
                    "summary": cols[4].text.strip(),
                    "link": cols[4].find("a")["href"] if cols[4].find("a") else ""
                })

        browser.close()
        return fines

# ✅ Write to JSON file
with open("gdpr_fines.json", "w") as f:
    json.dump(get_fines(), f, indent=2)
