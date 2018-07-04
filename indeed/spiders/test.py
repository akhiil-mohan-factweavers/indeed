import scrapy
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import SitemapSpider
from scrapy_redis.spiders import RedisSpider

from indeed.parse_items import parse_field


class MySpider(scrapy.Spider):
	name = 'test'
	start_urls = ['https://www.careerbuilder.co.in/jdp/dot-net-developer-j3n0g6704mvct3bd0h8']
	allowed_domains = ['www.careerbuilder.co.in']
	crawl_request = {
		"sitemap_urls": ["https://www.careerbuilder.co.in/sitemapindex.xml"],
		"website_name": "careerbuilder",
		"urlPattern": ["https://www.careerbuilder.co.in/jdp/"],
		"spider":"test",
		"fields": {
			"jobtitle": "h3 pb col big no-mb",
			"location": "fl-r fl-n-mobile",
			"company": "no-mb",
			"salary": "no-wrap"
		}
	}

	def parse(self, response):
		self.logger.info('sitemapspider|url in parse %s', response.url)
		print('response_url:', response.url)
		self.crawler.stats.inc_value('completed_url_careerbuilder', 1)
		response_value = 1
		temp = {'urls': []}
		tags = ['h1', 'div', 'a']
		item = parse_field(self.crawl_request, response, response_value, tags)
		print(len(item))
		if len(item) is not 0:
			yield item
		for link in LxmlLinkExtractor(allow_domains=self.allowed_domains).extract_links(response):
			url = response.urljoin(link.url)
			temp['urls'].append(url)
			yield scrapy.Request(url=url, callback=self.parse)
