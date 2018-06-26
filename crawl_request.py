import json
from urllib.parse import urlparse, urlencode


class CrawlRequest():
	allowed_domains = None
	start_urls = None
	crawl_request_string = None

	def _init__(self, request_string=None):
		if request_string is not None:
			self.crawl_request_string = request_string
			requestBody = json.loads(request_string)
