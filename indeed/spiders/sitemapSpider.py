from collections import defaultdict

import scrapy
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.utils.log import logger
from scrapy.spiders import SitemapSpider

from indeed.parse_items import parse_fields


class MySpider(SitemapSpider):
	name = 'sitemapspider'
	crawl_request = None
	allowed_domains = ['www.careerbuilder.co.in']
	custom_settings = {
		'CONCURRENT_REQUESTS': 8
	}

	def __init__(self, crawl_request=None):
		self.crawl_request = crawl_request
		if self.crawl_request is not None:
			self.sitemap_urls = crawl_request.get('sitemap_urls', None)
		self.logger.info("Crawl reqquest : %s " % self.crawl_request)
		super(MySpider, self).__init__()
		logger.info("intialized the sitemapspider spider")

	def start_requests(self):
		for sitemap_url in self.sitemap_urls:
			self.logger.info("Sitemap parse | url : %s" % sitemap_url)
			yield scrapy.Request(url=sitemap_url, callback=self._parse_sitemap)

	def parse(self, response):
		logger.info('sitemapspider|url in parse %s', response.url)
		self.crawler.stats.inc_value('completed_url', 1)
		self.crawler.stats.set_value('spider', 'careerbuilder')
		response_value = -2
		temp = {'urls': []}

		item = defaultdict(lambda: None)
		item = parse_fields(self.crawl_request, response, response_value)

		if item:
			yield item

		for link in LxmlLinkExtractor(allow_domains=self.allowed_domains).extract_links(response):
			url = response.urljoin(link.url)
			if str(url).find(self.crawl_request['urlPattern'][0]) >= 0:
				yield scrapy.Request(url=url, callback=self.parse)
