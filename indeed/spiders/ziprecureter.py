import os

import scrapy
from pip.utils import logging
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import Rule
from scrapy_redis.spiders import RedisSpider
from indeed.parse_items import parse_field, parse_links
from scrapy.utils.log import logger


class ZiprecruterSpider(scrapy.Spider):
	name = 'ziprecruter'
	allowed_domains = None
	start_urls = None
	crawl_request = None
	custom_settings = {
		'CONCURRENT_REQUESTS': 10
	}

	def __init__(self, crawl_request=None):
		self.crawl_request = crawl_request
		if self.crawl_request is not None:
			self.start_urls = crawl_request['start_urls']
			self.allowed_domains = crawl_request['allowed_domains']
		logger.info("intialized the ziprecruter spider")

	def start_requests(self):
		for url in self.start_urls:
			self.logger.info('ziprecruter|started parsing url : %s',url)
			yield scrapy.Request(url=url, callback=self.parse)

	def parse(self, response):
		logger.info('job_scrapper|url in parse : %s', response.url)
		self.crawler.stats.inc_value('completed_url', 1)
		self.crawler.stats.set_value('spider','ziprecruter')
		temp = {'urls': []}
		tags = ['h1','a','span']
		response_value = -2
		parse_response = parse_links(self.crawl_request, response, response_value, tags)
		print(parse_response)
		if parse_response is not None:
			if parse_response['type'] == 'links':
				links = parse_response.get('content')
				for link in links:
					url = response.urljoin(link)
					yield scrapy.Request(url=url, callback=self.parse)

			else:
				item = parse_response.get('content')
				if len(item) is not 0:
					yield item
