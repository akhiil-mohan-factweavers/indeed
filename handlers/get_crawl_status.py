from handlers.BaseHandler import BaseHandler
import  crawler_handler

class GetCrawlerStats(BaseHandler):
	crawlerHandler = crawler_handler

	def get(self):
		crawlerStats=self.crawlerHandler.getCrawlStatus()
		self.write(crawlerStats)