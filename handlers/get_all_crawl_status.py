from handlers.BaseHandler import BaseHandler
import  crawler_handler

class GetAllCrawlerStats(BaseHandler):
	crawlerHandler = crawler_handler

	def get(self):
		crawlerStats=self.crawlerHandler.getAllcrawlstatus()
		self.write(crawlerStats)