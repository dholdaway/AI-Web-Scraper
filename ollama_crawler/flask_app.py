from flask import Flask, request, jsonify
import asyncio
import os
from playwright.async_api import async_playwright
from cve_crawl import get_google_results_playwright, get_google_results_selenium, get_chrome_driver

app = Flask(__name__)

# Define path to store URLs for each CVE
BASE_OUTPUT_DIR = "./cve_results/"

@app.route("/crawl", methods=["POST"])
def crawl_cve():
    data = request.json
    cve_id = data.get("cve_id")

    if not cve_id:
        return jsonify({"error": "CVE ID is required"}), 400

    # Ensure output directory exists
    cve_output_dir = os.path.join(BASE_OUTPUT_DIR, cve_id)
    os.makedirs(cve_output_dir, exist_ok=True)

    # Initiate the async crawl task
    asyncio.run(start_google_crawl(cve_id, cve_output_dir))
    
    return jsonify({"status": "Crawling started", "cve_id": cve_id}), 202


async def start_google_crawl(cve_id, output_dir):
    urls_file = os.path.join(output_dir, "urls", "urls.txt")
    os.makedirs(os.path.dirname(urls_file), exist_ok=True)

    all_links = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for page in range(3):  # Search 3 pages
            links = await get_google_results_playwright(cve_id, page, browser)
            if not links:  # Fallback to Selenium if Playwright fails
                driver = get_chrome_driver()
                links = get_google_results_selenium(cve_id, page, driver)
                driver.quit()
            all_links.extend(links)
        await browser.close()

    # Save URLs to a file for Scrapy processing
    with open(urls_file, "w") as f:
        f.write("\n".join(all_links))

    print(f"URLs for {cve_id} saved to {urls_file}")


# Start the Flask app if the script is run directly
if __name__ == "__main__":
    app.run(debug=True)
