import json
import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError

URL = "https://www.enforcementtracker.com/"

def get_fines():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("Navigating to Enforcement Tracker...")
        page.goto(URL, wait_until="networkidle", timeout=120000)

        try:
            page.wait_for_selector("table#enforcementtable", timeout=90000, state="visible")
        except TimeoutError:
            print("❌ TimeoutError: enforcement table not found.")
            with open("page_snapshot.html", "w", encoding="utf-8") as snapshot:
                snapshot.write(page.content())
            browser.close()
            raise RuntimeError("Table not found on Enforcement Tracker. See page_snapshot.html for HTML dump.")

        print("✅ Table loaded. Parsing content...")
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

if __name__ == "__main__":
    print("⚙️ Starting scrape...")
    fines = get_fines()
    print(f"✅ Scraped {len(fines)} fines.")
    with open("gdpr_fines.json", "w", encoding="utf-8") as f:
        json.dump(fines, f, indent=2)
