import os

import scrapy
from pip.utils import logging
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import Rule
from scrapy_redis.spiders import RedisSpider
from indeed.parse_items import parse_field
from scrapy.utils.log import logger


class IndeedSpider(scrapy.Spider):
	name = 'job_scrapper'
	allowed_domains = None
	start_urls = None
	crawl_request = None

	def __init__(self, crawl_request=None):
		self.crawl_request = crawl_request
		if self.crawl_request is not None:
			self.start_urls = crawl_request['start_urls']
			self.allowed_domains = crawl_request['allowed_domains']
		logger.info("intialized the job_scraper spider")

	def start_requests(self):
		for url in self.start_urls:
			self.logger.info('job_scrapper|started parsing url : %s',url)
			yield scrapy.Request(url=url, callback=self.parse)

	def parse(self, response):
		logger.info('job_scrapper|url in parse : %s', response.url)
		self.crawler.stats.inc_value('completed_url', 1)
		response_value=1
		temp = {'urls': []}
		tags = ['span','b']
		response_value = -2
		item = parse_field(self.crawl_request,response,response_value,tags)
		if len(item)is not 0:
			yield item
		for link in LxmlLinkExtractor(allow_domains=self.allowed_domains).extract_links(response):
			url = response.urljoin(link.url)
			temp['urls'].append(url)
			yield scrapy.Request(url=url, callback=self.parse)
