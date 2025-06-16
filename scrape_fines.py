import json
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

URL = "https://www.enforcementtracker.com/"

def get_fines():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-gpu"])
        page = browser.new_page()

        print("Navigating to enforcement tracker...")
        page.goto(URL, timeout=60000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)

        print("Getting page content...")
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
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
    fines = get_fines()
    with open("public/gdpr_fines.json", "w", encoding="utf-8") as f:
        json.dump(fines, f, indent=2, ensure_ascii=False)
