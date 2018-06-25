import scrapy
from scrapy.selector import HtmlXPathSelector
from urllib.parse import urljoin


class BlogSpider(scrapy.Spider):
	name = 'indeed'
	allowed_domains = ['www.linkedin.com']
	start_urls = ['https://www.linkedin.com/']

	def parse(self, response):
		print('url', response.url)
		urls = response.xpath('//a/@href').extract()
		title = response.xpath('//title/text()').extract()
		h1_tag = response.xpath('//h1/text()').extract()
		h2_tag = response.xpath('//html/body/h2/text()').extract()
		p_tag = response.xpath('//p/text()').extract()
		if title:
			title = title[0]
		if h1_tag:
			h1_tag = h1_tag[0]
		if h2_tag:
			h2_tag = h2_tag[0]
		if p_tag:
			p_tag = p_tag[0]

		item = {}
		item['url'] = response.url
		item['title'] = title
		item['status'] = response.status
		item['h1_tag'] = h1_tag
		item['h2_tag'] = h2_tag
		item['p_tag'] = p_tag
		item['links'] = []
		for url in urls:
			url = response.urljoin(url)
			item['links'].append(url)
			yield scrapy.Request(url=url, callback=self.parse)

		yield item
