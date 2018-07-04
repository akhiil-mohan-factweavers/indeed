import json
import traceback
import tornado.web
from tornado import web


class BaseHandler(tornado.web.RequestHandler):


	def get(self):
		self.write("say something")

	def options(self):
		self.write("options")
		self.finish()

	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers",
		                "x-requested-with,Content-Type, Depth, User-Agent, X-File-Size,X-Requested-With, X-Requested-By, If-Modified-Since, X-File-Name, Cache-Control")
		self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")

	def write_error(self, status_code, **kwargs):

		self.set_header('Content-Type', 'application/json')
		if "exc_info" in kwargs:
			print(traceback.format_exception(*kwargs["exc_info"]))

		if self.settings.get("serve_traceback") and "exc_info" in kwargs:
			# in debug mode, try to send a traceback
			lines = []
			for line in traceback.format_exception(*kwargs["exc_info"]):
				lines.append(line)
			self.finish(json.dumps({
				'error': {
					'code': status_code,
					'message': self._reason,
					'traceback': lines,
				}
			}))
		else:
			self.finish(json.dumps({
				'error': {
					'code': status_code,
					'message': self._reason,
				}
			}))

