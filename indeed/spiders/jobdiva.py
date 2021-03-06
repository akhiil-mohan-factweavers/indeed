import scrapy
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.utils.log import logger
from scrapy.spiders import SitemapSpider

from indeed.parse_items import  parse_fields


class MySpider(SitemapSpider):
	name = 'jobdiva'
	crawl_request = None
	ifram_url = None
	allowed_domains = ['www.jobdiva.com','www1.jobdiva.com']
	custom_settings = {
		'CONCURRENT_REQUESTS':7
	}

	def __init__(self, crawl_request=None):
		self.crawl_request = crawl_request
		if self.crawl_request is not None:
			self.sitemap_urls = crawl_request.get('sitemap_urls', None)
		self.logger.info("Crawl reqquest : %s " % self.crawl_request)
		super(MySpider, self).__init__()
		logger.info("intialized the jobdiva spider")

	def start_requests(self):
		for sitemap_url in self.sitemap_urls:
			self.logger.info("Sitemap parse | url : %s" % sitemap_url)
			yield scrapy.Request(url=sitemap_url, callback=self._parse_sitemap)



	def parse(self, response):
		logger.info('jobdiva|url in parse %s', response.url)
		self.crawler.stats.inc_value('completed_url', 1)
		self.crawler.stats.set_value('spider', 'jobdiva')
		response_value =-2
		temp = {'urls': []}
		tags = ['span', 'td']
		item = parse_fields(self.crawl_request, response, response_value, tags)
		iframe_url =response.css('iframe::attr(src)').extract()

		for url in iframe_url:
			for allowed_domain in self.allowed_domains:
				response_value = url.find(allowed_domain)
				if response_value >= 0:
					yield scrapy.Request(url=url, callback=self.parse)
		if len(item) is not 0:
			yield item
		for link in LxmlLinkExtractor(allow_domains=self.allowed_domains).extract_links(response):

			url = response.urljoin(link.url)
			temp['urls'].append(url)
			yield scrapy.Request(url=url, callback=self.parse)





