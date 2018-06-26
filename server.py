import json

from urllib.parse import urlparse

from scrapy.crawler import CrawlerRunner, CrawlerProcess
from twisted.internet import reactor

from crawl_request import CrawlRequest
from indeed.spiders.indeed import IndeedSpider

url = 'https://www.ziprecruiter.com/'
process = CrawlerProcess()
start_urls = []
start_urls.append(url)
allowed_domains = []
for start_url in start_urls:
        domains = urlparse(start_url).netloc
        allowed_domains.append(domains)
crawl_request = {'start_url': start_url,'allowed_domains': allowed_domains,'spider': 'indeed'}
process.crawl(IndeedSpider,start_url=crawl_request['start_url'],allowed_domains=crawl_request['allowed_domains'])
process.start()
