import json
import os
import threading
from urllib.parse import urlparse

from pip.utils import  logger
from scrapy.crawler import CrawlerRunner
from scrapy.settings import Settings
from twisted.internet import reactor
import datetime
from scrapy.utils.log import configure_logging
from indeed import settings as my_settings
from indeed.util.util import total_time_in_second

process = None
starting_url = None
crawl_state = None
currentJob = None
crawler = None
runner = None
crawler1 = None
crawler2 = None
scrapy_response_career = None
scrapy_response_indeed = None
scrapy_response_jobdiv = None
def startCrawl():
	global process
	global starting_url
	global crawl_state
	global currentJob
	global crawler
	global runner
	global crawler1
	global crawler2
	crawler_settings = Settings()
	crawler_settings.setmodule(my_settings)
	runner = CrawlerRunner(settings=crawler_settings)
	configure_logging()
	try:
		with open("/home/lenovo/projects_python/indeed_new_1/scrapy_config/indeed_conf",
		          "r") as spider_config_file:
			crawl_request = spider_config_file.read().replace('\n', '')
		updated_request_json = {}
		crawl_request_json = json.loads(str(crawl_request))
		crawl_request_json['allowed_domains'] = []
		if 'start_urls' in crawl_request_json and crawl_request_json['start_urls'] is not None:
			for url in crawl_request_json['start_urls']:
				updated_request_json = parse_domain(url, crawl_request_json)
			crawl_request_json['spider'] = 'job_scrapper'
		print(updated_request_json)
		currentJob = updated_request_json

		deferred =runner.crawl(currentJob['spider'], currentJob)
		logger.info('indeed job added')
		with open("/home/lenovo/projects_python/indeed_new_1/scrapy_config/career_builder",
		          "r") as spider_config_file:
			crawl_request = spider_config_file.read().replace('\n', '')
		crawl_request_json = json.loads(str(crawl_request))
		crawl_request_json['spider'] = 'sitemapspider'
		print(crawl_request_json)
		currentJob = crawl_request_json

		deferred =runner.crawl(currentJob['spider'], currentJob)

		logger.info('career builder job added')

		'''with open("/home/lenovo/projects_python/indeed_new_1/scrapy_config/jobdiva","r") as spider_config_file:
			crawl_request = spider_config_file.read().replace('\n', '')
		crawl_request_json = json.loads(str(crawl_request))
		crawl_request_json['spider'] = 'jobdiva'
		print(crawl_request_json)
		currentJob = crawl_request_json
		deferred = runner.crawl(currentJob['spider'], currentJob)

		logger.info('jobdiva job added')'''

		d = runner.join()
		d.addBoth(lambda _: reactor.stop())
		threading._start_new_thread(reactor.run, ((),))
		crawl_state = "RUNNING"
		if list(runner.crawlers):
			print(runner.crawlers)
			crawler = list(runner.crawlers)[0]
			crawler1 =list(runner.crawlers)[1]
			#crawler2 = list(runner.crawlers)[0]

	except Exception as e:
		logger.error('crawler handler|spider : %s|error : %s',crawl_request['spider'],e)




def getCrawlStatus():
	global scrapy_response_career
	global scrapy_response_indeed
	global scrapy_response_jobdiv

	crawler_status = {}
	if crawler is not None:
		if crawler.stats.get_stats().copy() :
			print(crawler.stats.get_stats().copy())
			scrapy_response_career = crawler.stats.get_stats().copy()

		total_time = total_time_in_second(scrapy_response_career.get('start_time'))
		speed = scrapy_response_career['completed_url']/total_time
		scrapy_response_career['speed'] = speed
		scrapy_response_career['start_time'] = str(crawler.stats.get_stats().get('start_time'))
		if crawler1.stats.get_stats().copy():
			print(crawler.stats.get_stats().copy())
			scrapy_response_indeed = crawler1.stats.get_stats().copy()

		total_time = total_time_in_second(scrapy_response_indeed.get('start_time'))
		speed = scrapy_response_indeed['completed_url']/total_time
		scrapy_response_indeed['speed'] = speed
		scrapy_response_indeed['start_time'] = str(crawler1.stats.get_stats().get('start_time'))
		'''if crawler2.stats.get_stats().copy():
			print(crawler.stats.get_stats().copy())
			scrapy_response_jobdiv = crawler2.stats.get_stats().copy()

		total_time = total_time_in_second(scrapy_response_jobdiv.get('start_time'))
		speed = scrapy_response_jobdiv['completed_url'] / total_time
		scrapy_response_jobdiv['speed'] = speed
		scrapy_response_jobdiv['start_time'] = str(crawler2.stats.get_stats().get('start_time'))'''

		crawler_status["indeed"]=scrapy_response_career
		crawler_status['careerbudiler']=scrapy_response_indeed
		#crawler_status['Jobdiva']=scrapy_response_jobdiv
	else:
		status = {'status': 'no cralwer is running'}
		return status

	return crawler_status


def parse_domain(url, crawl_request_json):
	domains = urlparse(url).netloc
	crawl_request_json['allowed_domains'].append(domains)
	return crawl_request_json
