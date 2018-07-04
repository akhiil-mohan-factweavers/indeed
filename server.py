import json
import signal

from urllib.parse import urlparse
import tornado
from scrapy.utils.log import logger
from tornado import ioloop
from tornado import web

from scrapy.crawler import CrawlerRunner, CrawlerProcess
from scrapy.settings import Settings

import crawler_handler
from handlers.get_crawl_status import GetCrawlerStats
from indeed import settings as my_settings
from indeed.spiders.indeed import IndeedSpider


class JobScrapper(tornado.web.Application):
	request_url_patterns = [
		(r"/getCrawlStatus", GetCrawlerStats),
	]

	def __init__(self):
		tornado.web.Application.__init__(self, self.request_url_patterns, debug=False)


def main():
	app = JobScrapper()
	http_server = tornado.httpserver.HTTPServer(app)
	http_server.listen(8888)
	crawler_handler.startCrawl()
	logger.info('started the crawl at 8888')
	tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
	main()
