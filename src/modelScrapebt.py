from playwright.sync_api import sync_playwright, Playwright
from browserbase import Browserbase
import time

bb = Browserbase(api_key=os.environ["BROWSERBASE_API_KEY"])

BASE_URL = "https://platform.openai.com"

def run(playwright: Playwright):
    session = bb.sessions.create(project_id=os.environ["BROWSERBASE_PROJECT_ID"])
    chromium = playwright.chromium
    browser = chromium.connect_over_cdp(session.connect_url)
    context = browser.contexts[0]
    page = context.pages[0]

    try:
        # Step 1: Go to the overarching models page
        print("Navigating to models list page...")
        page.goto(f"{BASE_URL}/docs/models")
        page.wait_for_timeout(10000)

        # Step 2: Extract all model links
        model_links = set()
        # The links are typically <a href="/docs/models/xxx">
        anchors = page.query_selector_all('a[href^="/docs/models/"]')
        for anchor in anchors:
            href = anchor.get_attribute("href")
            # Filter to only the model doc links (not anchors like /docs/models#something)
            if href and href.startswith("/docs/models/") and "#" not in href:
                model_links.add(href)

        print(f"Found {len(model_links)} model pages:")
        for link in model_links:
            print(BASE_URL + link)

        # Step 3: Visit each model page and scrape
        for link in model_links:
            url = BASE_URL + link
            print(f"\nScraping: {url}")
            page.goto(url)
            page.wait_for_timeout(10000)
            body_text = page.inner_text("body")
            print(f"----- Content from {url} -----")
            print(body_text[:3000])
            print(f"----- End of content for {url} -----\n")
            # Optionally save:
            # with open(link.split("/")[-1] + ".txt", "w", encoding="utf-8") as f:
            #     f.write(body_text)
            time.sleep(2)  # Optional polite pause between requests

    finally:
        page.close()
        browser.close()
        print(f"Session complete! View replay at https://browserbase.com/sessions/{session.id}")

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
