from playwright.sync_api import sync_playwright, Playwright
from browserbase import Browserbase
import os
import time
import json
import datetime

bb = Browserbase(api_key=os.environ["BROWSERBASE_API_KEY"])
BASE_URL = "https://platform.openai.com"

def safe_filename(name):
    # Sanitize filename: remove slashes, spaces, etc.
    return name.replace("/", "_").replace(" ", "_")

def run(playwright: Playwright):
    # Set up timestamped run directory
    run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = f"model_html/{run_id}"
    os.makedirs(run_dir, exist_ok=True)

    session = bb.sessions.create(project_id=os.environ["BROWSERBASE_PROJECT_ID"])
    chromium = playwright.chromium
    browser = chromium.connect_over_cdp(session.connect_url)
    context = browser.contexts[0]
    page = context.pages[0]

    run_metadata = {
        "run_id": run_id,
        "datetime": datetime.datetime.now().isoformat(),
        "pages": [],
        "success": False
    }

    try:
        print("Navigating to models list page...")
        page.goto(f"{BASE_URL}/docs/models")
        page.wait_for_timeout(10000)

        # Extract all model links
        model_links = set()
        anchors = page.query_selector_all('a[href^="/docs/models/"]')
        for anchor in anchors:
            href = anchor.get_attribute("href")
            if href and href.startswith("/docs/models/") and "#" not in href:
                model_links.add(href)

        print(f"Found {len(model_links)} model pages.")

        # Visit each model page and scrape HTML
        for link in model_links:
            url = BASE_URL + link
            model_alias = link.split("/")[-1]
            filename = safe_filename(model_alias) + ".html"
            filepath = os.path.join(run_dir, filename)
            page_result = {
                "model_alias": model_alias,
                "url": url,
                "filename": filename
            }
            try:
                print(f"\nScraping: {url}")
                page.goto(url)
                page.wait_for_timeout(10000)
                html_content = page.content()
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(html_content)
                page_result["success"] = True
                print(f"Saved HTML to {filepath}")
            except Exception as e:
                page_result["success"] = False
                page_result["error"] = str(e)
                print(f"Failed to scrape {url}: {e}")
            run_metadata["pages"].append(page_result)
            time.sleep(2)  # Polite pause

        # Set overall run success
        run_metadata["success"] = all(p["success"] for p in run_metadata["pages"])

        # Save metadata
        meta_path = os.path.join(run_dir, "run_metadata.json")
        with open(meta_path, "w") as f:
            json.dump(run_metadata, f, indent=2)

        print(f"Metadata saved to {meta_path}")

    finally:
        page.close()
        browser.close()
        print(f"Session complete! View replay at https://browserbase.com/sessions/{session.id}")

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
