import json
import multiprocessing
import os
import requests
import threading
from urllib.parse import urlparse

from joblib import Parallel, delayed
from pip.utils import logger
from scrapy.crawler import CrawlerRunner
from scrapy.settings import Settings
from twisted.internet import reactor
import datetime
from scrapy.utils.log import configure_logging
from indeed import settings as my_settings
from indeed.util.util import total_time_in_second
import configparser

from utilities.utility import get_node_url

config = configparser.RawConfigParser()
config.read('scrapy.cfg')
path = config.get('configPath', 'path')

process = None
starting_url = None
crawl_state = None
currentJob = None
crawler = None
runner = None
crawler1 = None
crawler2 = None
crawler3 = None
scrapy_response_career = None
scrapy_response_indeed = None
scrapy_response_jobdiv = None
scrapy_response_jobdiv1 = None
scrapy_response_career1 = None
scrapy_response_indeed1 = None
scrapy_response_zip1 = None
scrapy_response_zip = None
scrapy_response_dice1 = None
scrapy_response_dice = None


def startCrawl():
	global process
	global starting_url
	global crawl_state
	global currentJob
	global crawler
	global runner
	global crawler1
	global crawler2
	global crawler3
	global crawler4

	crawler_settings = Settings()
	crawler_settings.setmodule(my_settings)
	runner = CrawlerRunner(settings=crawler_settings)
	configure_logging()

	try:
		add_spider_to_job("indeed_conf", 'job_scrapper')
		add_spider_to_job("ziprecruter", 'ziprecruter')
		add_spider_to_job("career_builder",'sitemapspider')
		add_spider_to_job("dice1", 'Dice1')

		d = runner.join()
		d.addBoth(lambda _: reactor.stop())
		threading._start_new_thread(reactor.run, ((),))

		crawl_state = "RUNNING"
		if list(runner.crawlers):
			crawler = list(runner.crawlers)[0]
			crawler1 = list(runner.crawlers)[1]
			crawler2 = list(runner.crawlers)[2]
			crawler3 = list(runner.crawlers)[3]
			#crawler4 = list(runner.crawlers)[4]

	except Exception as e:
		logger.error('crawler handler|error : %s', e)


def getAllcrawlstatus():
	other_machine = config.get('machine', 'Other_Machine')
	other_machine = other_machine.split(',')
	num_cores = multiprocessing.cpu_count()
	node_status_lists = Parallel(n_jobs=num_cores)(
		delayed(get_node_crawl_status)(machine_url) for machine_url in other_machine)

	node_status_lists.append(getCrawlStatus())
	spiders = []
	for machine in node_status_lists:
		for spider in machine.keys():
			if spider not in spiders:
				spiders.append(spider)

	finalJSON = {}
	for spider in spiders:
		speed = 0
		completed_url = 0
		enqued = 0
		count = 0
		status = []
		status_final = None
		for machine in node_status_lists:
			count += 1
			speed = speed + machine[spider]['speed']
			completed_url = completed_url + machine[spider]['completed_url']
			enqued = enqued + machine[spider]['scheduler/enqueued/redis']
			status.append(machine[spider]['status'])

		if 'RUNNING' in status:
			status_final = 'RUNNING'

		else:
			status_final = 'FINISHED'
		final_json_content = {'speed': speed, 'completed_url': completed_url, 'Enqued': enqued,'Status': status_final}
		finalJSON[spider] = final_json_content

	return finalJSON


def getCrawlStatus():
	global scrapy_response_career
	global scrapy_response_indeed
	global scrapy_response_career1
	global scrapy_response_indeed1
	global scrapy_response_jobdiv
	global scrapy_response_jobdiv1
	global scrapy_response_zip1
	global scrapy_response_zip
	global scrapy_response_dice1
	global crapy_response_dice
	crawler_status = {}
	if runner.crawlers is not None:
		try:
			if 'finish_time' in crawler.stats.get_stats().keys():

				temp_response = scrapy_response_indeed1.copy()
				current_time = crawler.stats.get_stats()['finish_time']
				total_time = total_time_in_second(temp_response.get('start_time'), current_time)
				temp_response['completed_url'] = crawler.stats.get_stats().get('completed_url')
				speed = temp_response['completed_url'] / total_time
				temp_response['speed'] = speed
				temp_response['start_time'] = str(temp_response.get('start_time'))
				temp_response['status'] = 'FINISHED'
				crawler_status[temp_response['spider']] = temp_response
			else:

				scrapy_response_indeed = crawler.stats.get_stats().copy()
				scrapy_response_indeed1 = crawler.stats.get_stats().copy()
				current_time = datetime.datetime.utcnow()
				total_time = total_time_in_second(scrapy_response_indeed.get('start_time'),
				                                  current_time)
				speed = scrapy_response_indeed['completed_url'] / total_time
				scrapy_response_indeed['speed'] = speed
				scrapy_response_indeed['start_time'] = str(scrapy_response_indeed.get('start_time'))
				scrapy_response_indeed['status'] = 'RUNNING'
				crawler_status[scrapy_response_indeed['spider']] = scrapy_response_indeed

			if 'finish_time' in crawler2.stats.get_stats().keys():
				temp_response = scrapy_response_jobdiv1.copy()
				current_time = crawler2.stats.get_stats()['finish_time']
				total_time = total_time_in_second(temp_response.get('start_time'), current_time)
				temp_response['completed_url'] = crawler2.stats.get_stats().get('completed_url')
				speed = temp_response['completed_url'] / total_time
				temp_response['speed'] = speed
				temp_response['start_time'] = str(temp_response.get('start_time'))
				temp_response['status'] = 'FINISHED'
				crawler_status[temp_response['spider']] = temp_response
			else:
	
				scrapy_response_jobdiv = crawler2.stats.get_stats().copy()
				scrapy_response_jobdiv1 = crawler2.stats.get_stats().copy()
				current_time = datetime.datetime.utcnow()
				total_time = total_time_in_second(scrapy_response_jobdiv.get('start_time'), current_time)
				speed = scrapy_response_jobdiv['completed_url'] / total_time
				scrapy_response_jobdiv['speed'] = speed
				scrapy_response_jobdiv['start_time'] = str(scrapy_response_jobdiv.get('start_time'))
				scrapy_response_jobdiv['status'] = 'RUNNING'
				crawler_status[scrapy_response_jobdiv['spider']] = scrapy_response_jobdiv
	
			if 'finish_time' in crawler1.stats.get_stats().keys():
	
				temp_response = scrapy_response_career1.copy()
				current_time = crawler1.stats.get_stats()['finish_time']
				total_time = total_time_in_second(temp_response.get('start_time'), current_time)
				temp_response['completed_url'] = crawler1.stats.get_stats().get('completed_url')
				speed = temp_response['completed_url'] / total_time
				temp_response['speed'] = speed
				temp_response['start_time'] = str(temp_response.get('start_time'))
				temp_response['status'] = 'FINISHED'
				crawler_status[temp_response['spider']] = temp_response
			else:
	
				scrapy_response_career = crawler1.stats.get_stats().copy()
				scrapy_response_career1 = crawler1.stats.get_stats().copy()
				current_time = datetime.datetime.utcnow()
				total_time = total_time_in_second(scrapy_response_career.get('start_time'), current_time)
				speed = scrapy_response_career['completed_url'] / total_time
				scrapy_response_career['speed'] = speed
				scrapy_response_career['start_time'] = str(scrapy_response_career.get('start_time'))
				scrapy_response_career['status'] = 'RUNNING'
				crawler_status[scrapy_response_career['spider']] = scrapy_response_career
	
			if 'finish_time' in crawler3.stats.get_stats().keys():
	
				temp_response = scrapy_response_zip1.copy()
				current_time = crawler3.stats.get_stats()['finish_time']
				total_time = total_time_in_second(temp_response.get('start_time'), current_time)
				temp_response['completed_url'] = crawler3.stats.get_stats().get('completed_url')
				speed = temp_response['completed_url'] / total_time
				temp_response['speed'] = speed
				temp_response['start_time'] = str(temp_response.get('start_time'))
				temp_response['status'] = 'FINISHED'
				crawler_status[temp_response['spider']] = temp_response
	
	
			else:
	
				scrapy_response_zip = crawler3.stats.get_stats().copy()
				scrapy_response_zip1 = crawler3.stats.get_stats().copy()
				current_time = datetime.datetime.utcnow()
				total_time = total_time_in_second(scrapy_response_zip.get('start_time'), current_time)
				speed = scrapy_response_zip['completed_url'] / total_time
				scrapy_response_zip['speed'] = speed
				scrapy_response_zip['start_time'] = str(scrapy_response_zip.get('start_time'))
				scrapy_response_zip['status'] = 'RUNNING'
				crawler_status[scrapy_response_zip['spider']] = scrapy_response_zip
	
			'''if 'finish_time' in crawler4.stats.get_stats().keys():
	
				temp_response = scrapy_response_dice1.copy()
				current_time = crawler4.stats.get_stats()['finish_time']
				total_time = total_time_in_second(temp_response.get('start_time'), current_time)
				temp_response['completed_url'] = crawler4.stats.get_stats().get('completed_url')
				speed = temp_response['completed_url'] / total_time
				temp_response['speed'] = speed
				temp_response['start_time'] = str(temp_response.get('start_time'))
				temp_response['status'] = 'FINISHED'
				crawler_status[temp_response['spider']] = temp_response
			else:
	
				scrapy_response_dice = crawler4.stats.get_stats().copy()
				scrapy_response_dice1 = crawler4.stats.get_stats().copy()
				current_time = datetime.datetime.utcnow()
				total_time = total_time_in_second(scrapy_response_dice.get('start_time'),current_time)
				speed = scrapy_response_dice['completed_url'] / total_time
				scrapy_response_dice['speed'] = speed
				scrapy_response_dice['start_time'] = str(scrapy_response_dice.get('start_time'))
				scrapy_response_dice['status']='RUNNING'
				crawler_status[scrapy_response_dice['spider']] = scrapy_response_dice'''

		except Exception as e:

			status = {'status': e}




	else:
		status = {'status': 'no cralwer is running'}
		return status

	return crawler_status


def parse_domain(url, crawl_request_json):
	domains = urlparse(url).netloc
	crawl_request_json['allowed_domains'].append(domains)
	return crawl_request_json


def add_spider_to_job(filename, spider):
	global path
	filepath = path + filename
	with open(filepath, "r") as spider_config_file:
		crawl_request = spider_config_file.read().replace('\n', '')
	updated_request_json = {}
	crawl_request_json = json.loads(str(crawl_request))
	crawl_request_json['spider'] = spider

	if 'start_urls' in crawl_request_json and crawl_request_json['start_urls'] is not None:
		crawl_request_json['allowed_domains'] = []
		for url in crawl_request_json['start_urls']:
			updated_request_json = parse_domain(url, crawl_request_json)

	if len(updated_request_json) is not 0:
		currentJob = updated_request_json
	else:
		currentJob = crawl_request_json
	print(currentJob)
	deferred = runner.crawl(currentJob['spider'], currentJob)

	logger.info('%s job added', spider)


def get_node_crawl_status(machine_url):
	url = get_node_url(machine_url) + '/getCrawlStatus'
	http_response = requests.get(url)
	if http_response.status_code == 200:
		return http_response.json()
