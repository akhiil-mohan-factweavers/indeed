import json

from urllib.parse import urlparse

from scrapy.crawler import CrawlerRunner, CrawlerProcess
from scrapy.settings import Settings
from indeed import settings as my_settings
from indeed.spiders.indeed import IndeedSpider
from indeed.spiders.test import TestSpider
crawler_settings = Settings()
crawler_settings.setmodule(my_settings)
url = 'https://www.ziprecruiter.com/'
process = CrawlerProcess(settings=crawler_settings)
start_urls = []
start_urls.append(url)
allowed_domains = []
for start_url in start_urls:
        domains = urlparse(start_url).netloc
        allowed_domains.append(domains)
crawl_request = {'start_url': start_url,'allowed_domains': allowed_domains,'spider': 'indeed'}
process.crawl(IndeedSpider,start_url =start_url,allowed_domains = allowed_domains)
process.start()
