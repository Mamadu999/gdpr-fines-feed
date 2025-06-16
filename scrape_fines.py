from playwright.sync_api import sync_playwright
import json
import time

def get_fines():
    url = "https://www.enforcementtracker.com/"
    print("🔄 Launching browser...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("🌐 Navigating to Enforcement Tracker...")
        page.goto(url, timeout=120000)

        try:
            page.wait_for_selector("table#enforcementtable", timeout=90000, state="visible")
            print("✅ Table found, scraping...")

            # JavaScript to extract all data
            data = page.evaluate("""
                () => {
                    const rows = Array.from(document.querySelectorAll("table#enforcementtable tbody tr"));
                    return rows.map(row => {
                        const cells = row.querySelectorAll("td");
                        return {
                            date: cells[0]?.innerText.trim(),
                            country: cells[1]?.innerText.trim(),
                            authority: cells[2]?.innerText.trim(),
                            company: cells[3]?.innerText.trim(),
                            sector: cells[4]?.innerText.trim(),
                            fine: cells[5]?.innerText.trim(),
                            summary: cells[6]?.innerText.trim(),
                            link: row.querySelector("a")?.href || null
                        };
                    });
                }
            """)
            print(f"📊 Scraped {len(data)} fine records.")
        except Exception as e:
            print(f"❌ Timeout or error: {str(e)}")
            print("🩺 Saving full page snapshot for debugging...")
            html = page.content()
            with open("page_snapshot.html", "w", encoding="utf-8") as f:
                f.write(html)
            raise RuntimeError("⚠️ Table not found. Snapshot saved to page_snapshot.html.")

        browser.close()
        return data

if __name__ == "__main__":
    print("⚙️ Starting GDPR fines scrape...")
    fines = get_fines()
    with open("gdpr_fines.json", "w", encoding="utf-8") as f:
        json.dump(fines, f, indent=2, ensure_ascii=False)
    print("✅ Done. Data saved to gdpr_fines.json.")
