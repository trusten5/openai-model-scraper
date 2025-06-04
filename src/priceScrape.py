from playwright.sync_api import sync_playwright, Playwright
from browserbase import Browserbase
import re

bb = Browserbase(api_key=os.environ["BROWSERBASE_API_KEY"])

def run(playwright: Playwright):
    # Create a session on Browserbase
    session = bb.sessions.create(project_id=os.environ["BROWSERBASE_PROJECT_ID"])

    # Connect to the remote session
    chromium = playwright.chromium
    browser = chromium.connect_over_cdp(session.connect_url)
    context = browser.contexts[0]
    page = context.pages[0]

    try:
        page.goto("https://platform.openai.com/docs/pricing")
        page.wait_for_timeout(10000)  # Wait for dynamic content

        # Get all text in the body and code blocks
        body_text = page.inner_text("body")
        code_elements = page.query_selector_all("code")
        code_text = "\n".join([el.inner_text() for el in code_elements])
        all_text = body_text + "\n" + code_text

        # Regex to find model IDs (must have at least one dash and 6+ chars)
        pattern = re.compile(r'\b(?=\w*-)\w[\w\-\.]{5,}\b')
        model_ids = sorted(set(pattern.findall(all_text)))

        # Filter: Only output IDs that
        # - are NOT substrings of any longer match (i.e., are maximal)
        # - AND contain another, shorter candidate as a substring
        filtered_ids = []
        for candidate in model_ids:
            has_substring = any(
                candidate != other and other in candidate for other in model_ids
            )
            is_not_substring = not any(
                candidate != other and candidate in other for other in model_ids
            )
            if has_substring and is_not_substring:
                filtered_ids.append(candidate)

        print("Filtered Model IDs:")
        for model_id in filtered_ids:
            print(model_id)

    finally:
        page.close()
        browser.close()
        print(f"Session complete! View replay at https://browserbase.com/sessions/{session.id}")

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
