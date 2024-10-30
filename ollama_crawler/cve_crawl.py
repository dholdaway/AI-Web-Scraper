import time
import random
from fake_useragent import UserAgent
from scrapy import Selector
from playwright.async_api import async_playwright
import undetected_chromedriver as uc

user_agent = UserAgent()

async def get_google_results_playwright(cve_id, page, browser):
    context = await browser.new_context(user_agent=user_agent.random)
    page_obj = await context.new_page()

    search_query = f"https://www.google.com/search?q={cve_id}&start={page * 10}"
    await page_obj.goto(search_query, timeout=60000)
    search_results = await page_obj.query_selector_all("div.g")

    links = []
    for result in search_results:
        link_element = await result.query_selector("a")
        if link_element:
            link = await link_element.get_attribute("href")
            if link:
                links.append(link)

    await context.close()
    return links

def get_google_results_selenium(cve_id, page, driver):
    search_query = f"https://www.google.com/search?q={cve_id}&start={page * 10}"
    driver.get(search_query)
    time.sleep(random.uniform(2, 5))

    html = driver.page_source
    selector = Selector(text=html)
    search_results = selector.css('div.g')

    links = [result.css('a::attr(href)').get() for result in search_results]
    return links

def get_chrome_driver():
    options = uc.ChromeOptions()
    options.add_argument(f"user-agent={user_agent.random}")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    driver = uc.Chrome(options=options)
    return driver
