import scrapy
import os
from bs4 import BeautifulSoup
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from urllib.parse import urlparse

class CVECrawlSpider(CrawlSpider):
    name = 'cve_crawl_spider'

    rules = (
        Rule(LinkExtractor(), callback='parse_item', follow=True),
    )

    def __init__(self, cve_folder='', max_depth=2, *args, **kwargs):
        super(CVECrawlSpider, self).__init__(*args, **kwargs)
        self.cve_folder = cve_folder
        self.max_depth = int(max_depth)
        self.new_urls = set()

        # Define directories for organized results
        self.urls_dir = os.path.join(self.cve_folder, 'urls')
        self.content_dir = os.path.join(self.cve_folder, 'content')
        self.secondary_content_dir = os.path.join(self.cve_folder, 'secondary_content')
        self.logs_dir = os.path.join(self.cve_folder, 'logs')

        # Create directories if they don't exist
        os.makedirs(self.urls_dir, exist_ok=True)
        os.makedirs(self.content_dir, exist_ok=True)
        os.makedirs(self.secondary_content_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)

        # Log the start of the crawl
        self.logger.info(f"Crawling started for {cve_folder}")

    def start_requests(self):
        urls_file = os.path.join(self.urls_dir, 'urls.txt')
        with open(urls_file, 'r') as f:
            urls = f.readlines()
            for url in urls:
                yield scrapy.Request(url.strip(), callback=self.parse_item, meta={'depth': 1})

    def parse_item(self, response):
        title = response.css('title::text').get()
        body = response.css('body').get()
        
        # Save primary content to content directory
        if body:
            cleaned_body = self.clean_html(body)
            filename = os.path.join(self.content_dir, f"{response.url.split('/')[-1]}_solution.txt")
            with open(filename, 'a') as f:
                f.write(f"Title: {title}\n")
                f.write(f"URL: {response.url}\n\n")
                f.write(cleaned_body + "\n\n")

        # Follow additional links within max depth
        current_depth = response.meta.get('depth', 1)
        if current_depth < self.max_depth:
            yield from self.crawl_secondary_urls(response, current_depth + 1)

    def crawl_secondary_urls(self, response, depth):
        links = LinkExtractor().extract_links(response)
        for link in links:
            domain = urlparse(link.url).netloc
            path = urlparse(link.url).path

            if link.url not in self.new_urls and self.is_valid_path(path):
                self.new_urls.add(link.url)
                # Save secondary content to secondary_content directory
                yield scrapy.Request(link.url, callback=self.parse_secondary, meta={'depth': depth})

    def parse_secondary(self, response):
        title = response.css('title::text').get()
        body = response.css('body').get()

        if body:
            cleaned_body = self.clean_html(body)
            filename = os.path.join(self.secondary_content_dir, f"{response.url.split('/')[-1]}_secondary.txt")
            with open(filename, 'w') as f:
                f.write(f"Title: {title}\n")
                f.write(f"URL: {response.url}\n\n")
                f.write(cleaned_body + "\n\n")

    def clean_html(self, raw_html):
        soup = BeautifulSoup(raw_html, 'html.parser')
        for script_or_style in soup(['script', 'style']):
            script_or_style.extract()
        text = soup.get_text()
        return text.strip()

    def is_valid_path(self, path):
        excluded_paths = [
            "/privacy", "/contact", "/about", "/terms", "/faq", "/support", "/jobs", "/login", "/register"
        ]
        return not any(excluded in path for excluded in excluded_paths)
