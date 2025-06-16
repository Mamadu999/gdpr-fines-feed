import json
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

URL = "https://www.enforcementtracker.com/"

def get_fines():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        page.goto(URL, timeout=60000)
        page.wait_for_selector("table#enforcementtable", timeout=60000, state="visible")

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

with open("public/gdpr_fines.json", "w") as f:
    json.dump(get_fines(), f, indent=2)
