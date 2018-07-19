import datetime
import os
import re
import urllib

import scrapy
from bs4 import BeautifulSoup
from scrapy.utils.log import logger


def parse_links(crawl_request, response, response_value, tags):
	links = []
	links_html = []
	urlPatterns = crawl_request.get('urlPattern', None)
	match_value = -2
	soup = BeautifulSoup(response.text, "html.parser")
	for urlPattern in urlPatterns:
		print(urlPattern)
		for pattern in urlPattern.get('pattern', None):
			match_value = str(response.url).find(pattern)
			print(match_value)
			if pattern == 'https://www.indeed.co.in/browsejobs':
				if pattern == str(response.url):
					match_value = 0
				else:
					match_value = -2
			if match_value >= 0:
				break
		if match_value >= 0:
			if urlPattern['followOnly'] == 'true':
				if urlPattern['jobpage'] == 'yes':
					sel_htmls = soup.find_all(urlPattern['css-sel'], {
						urlPattern['tag-name']: urlPattern['extrackURLFrom']})
					for sel_html in sel_htmls:
						if urlPattern['direct_links'] == 'no':
							a_tag = sel_html.find('a')
							if a_tag is not None:
								links.append(sel_html.a['href'])
						else:
							links.append(sel_html['href'])

					if crawl_request['spider'] == 'job_scrapper':
						pagination = soup.find('div', {'class': 'pagination'})
						links_html = pagination.find_all('a', href=True)
						for link_html in links_html:
							if link_html['href'] not in links:
								links.append(link_html['href'])
				else:
					sel_html = soup.find(urlPattern['css-sel'],
					                     {urlPattern['tag-name']: urlPattern['extrackURLFrom']})
					links_html = sel_html.find_all('a', href=True)
					for link_html in links_html:
						links.append(link_html['href'])

				return {'type': 'links', 'content': links}
			else:

				temp_crawl_request = {'fields': urlPattern['fields'], 'spider': crawl_request['spider'],
				                      'urlPattern': urlPattern['pattern'],
				                      'website_name': crawl_request['website_name'],
				                      'tags_name': urlPattern['tags_name']}
				item = {}
				item = parse_fields(temp_crawl_request, response, response_value, tags)
				print('items::::::::::', item)
				return {'type': 'items', 'content': item}


def url_lib_request(url):
	respose = urllib.urlopen(url)
	soup = BeautifulSoup(respose)
	return soup


def parse_fields(crawl_request, response, response_value, tags):
	item = {}
	fields = crawl_request.get('fields', None)
	tags_name = crawl_request.get('tags_name', None)
	response_html = response.body.decode("utf-8")
	soup = BeautifulSoup(response_html, "html.parser")
	for url_pattern in crawl_request['urlPattern']:
		response_value = str(response.url).find(url_pattern)

		if response_value >= 0:
			break
	if response_value >= 0:
		try:
			flag_status = 0

			if soup.find(tags[0], {tags_name[0]: fields['company']}):
				item['company'] = soup.find(tags[0], {tags_name[0]: fields['company']}).text.strip()
				flag_status = flag_status + 1

			if soup.find(tags[1], {tags_name[1]: fields['jobtitle']}):
				item['jobtitle'] = soup.find(tags[1], {tags_name[1]: fields['jobtitle']}).text.strip()
				flag_status = flag_status + 1

			if soup.find(tags[2], {tags_name[2]: fields['location']}):
				item['location'] = soup.find(tags[2], {tags_name[2]: fields['location']}).text.strip()
				flag_status = flag_status + 1

			if soup.find(tags[3], {tags_name[3]: fields['salary']}):
				item['compensation'] = soup.find(tags[3], {tags_name[3]: fields['salary']}).text.strip()
				flag_status = flag_status + 1

			if soup.find(tags[4], {tags_name[4]: fields['posted_date']}):
				item['posted'] = soup.find(tags[4], {tags_name[4]: fields['posted_date']}).text.strip()
				flag_status = flag_status + 1

			if soup.select(fields['jobtype']):
				job_type = soup.select(fields['jobtype'])
				if crawl_request['spider'] == 'Dice' or crawl_request['spider'] == 'Dice1':
					item['employment_type'] = job_type[0].get('value').strip()
					flag_status = flag_status + 1
				elif crawl_request['spider'] == 'sitemapspider':
					item['employment_type'] = job_type[0].text.strip()
					flag_status = flag_status + 1
				elif crawl_request['spider'] == 'ziprecruter':
					item['employment_type'] = job_type[0].text.strip()
					flag_status = flag_status + 1

			if soup.find(tags[6], {tags_name[6]: fields['applylink']}):
				apply_link = soup.find('a', {'class': fields['applylink']})['href']
				item['Link/Mechanism_to_apply_the_job'] = response.urljoin(apply_link)
				flag_status = flag_status + 1

			if soup.find(tags[7], {tags_name[7]: fields['posted_by']}):
				item['posted_by'] = soup.find(tags[7], {tags_name[7]: fields['posted_by']}).text.strip()
				flag_status = flag_status + 1

			if flag_status > 1:
				item['website_name'] = crawl_request['website_name']
				item['date_of_scraped'] = str(datetime.datetime.utcnow())
				item['url'] = response.url

			if crawl_request.get('spider') == 'ziprecruter':
				item, flag_status = ziprecruter_description_parse(soup, item, flag_status)

			if crawl_request.get('spider') == 'Dice' or crawl_request.get('spider') == 'Dice1':
				item, flag_status = dice_description_parse(soup, item, flag_status)




		except Exception as e:
			logger.error('parse_items|spider :%s|error : %s', crawl_request['spider'], e)
	return item


def ziprecruter_description_parse(soup, item, flag_status):
	job_divs = soup.find_all('div', class_='jobDescriptionSection')
	for div in job_divs:
		ptags = ""
		ptag = div.select('div p')
		for p in ptag:
			ptags = ptags + p.get_text()
		item["jobDescription"] = ptags
		flag_status = flag_status + 1

	return item,flag_status

def dice_description_parse(soup, item, flag_status):
	jobDescription = soup.find_all('div',{'itemprop':'description'})
	if jobDescription:
		item["job_description"] = jobDescription[0].get_text().strip()
		flag_status = flag_status + 1

	return item, flag_status


