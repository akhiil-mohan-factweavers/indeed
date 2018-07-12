import datetime
import os
import urllib

import scrapy
from bs4 import BeautifulSoup
from scrapy.utils.log import logger


def parse_field(crawl_request, response, response_value, tags):
	item = {}
	fields = crawl_request.get('fields', None)
	soup = BeautifulSoup(response.text, "html.parser")
	for url_pattern in crawl_request['urlPattern']:
		response_value = str(response.url).find(url_pattern)

		if response_value >= 0:
			break
	if response_value >= 0:
		try:
			flag_indeed = 0
			flag_career = 0
			flag_jobdiva = 0
			flag_ziprecruter = 0

			if crawl_request['spider'] == 'job_scrapper':
				if soup.find(tags[0], {'class': fields['company']}):
					item['company'] = soup.find(tags[0], {'class': fields['company']}).text
					flag_indeed = flag_indeed + 1

				if soup.find(tags[1], {'class': fields['jobtitle']}):
					item['jobtitle'] = soup.find(tags[1], {'class': fields['jobtitle']}).text
					flag_indeed = flag_indeed + 1

				if soup.find(tags[0], {'class': fields['location']}):
					item['location'] = soup.find(tags[0], {'class': fields['location']}).text
					flag_indeed = flag_indeed + 1

				if soup.find(tags[0], {'class': fields['salary']}):
					item['salary'] = soup.find(tags[0], {'class': fields['salary']}).text.strip()
					flag_indeed = flag_indeed + 1
				if soup.find('span', {'class':'date'}):
					item['date_of_job_posted']=soup.find('span', {'class':'date'}).text.strip()
					flag_indeed = flag_indeed + 1

				'''if soup.find(tags[2], {'class':fields['companydes']}):
					companyreview =soup.find(tags[2], {'class':fields['companydes']})
					if companyreview.find('a',href=True):
						link = companyreview.find('a',href=True)['href']
						comp_url = response.urljoin(link)
						companyreview=url_lib_request(comp_url)
						if companyreview.find('span', {'class': 'cmp-header-rating-average'}):
							CompanyRating=companyreview.find('span', {'class': 'cmp-header-rating-average'}).text
							item['MYC-CompanyRating']=CompanyRating
							flag_indeed = flag_indeed + 1
						if companyreview.soup.find('li', {'class':'cmp-menu--reviews'}):
							review_link = soup.find('li', {'class':'cmp-menu--reviews'})
							if review_link.find('a',href=True):
								link = review_link.find('a', href=True)['href']
								link = response.urljoin(link)
								review = url_lib_request(link)'''



			elif crawl_request['spider'] == 'sitemapspider':

				if soup.find(tags[2], {'class': fields['company']}):
					company = soup.find(tags[2], {'class': fields['company']}).text.strip()
					item['company'] = company.split("posted by ", 1)[1]
					flag_career = flag_career + 1

				if soup.find(tags[0], {'class': fields['jobtitle']}):
					job_title = soup.find(tags[0], {'class': fields['jobtitle']}).text.strip()
					item['jobtitle'] = job_title.split("\n", 1)[0]
					flag_career = flag_career + 1

				if soup.find(tags[1], {'class': fields['location']}):
					item['location'] = soup.find(tags[1],
					                             {'class': fields['location']}).text.strip()
					flag_career = flag_career + 1

				if soup.find(tags[1], {'class':fields['jobtype']}):
					item['jobtype'] = soup.find('div', {'class':'fl-l fl-n-mobile'}).text.strip()
					flag_career = flag_career + 1

				if soup.find('a', {'class': 'btn btn-apply'}):
					apply_link = soup.find('a', {'class':'btn btn-apply'})['href']
					item['Link/Mechanism_to_apply_the_job']=response.urljoin(apply_link)
					flag_career = flag_career + 1

			elif crawl_request['spider'] == 'jobdiva':

				if soup.find(tags[0], {'style': 'text-align:center; vertical-align:top; '}):
					job_title = soup.find(tags[0],
					                      {'style': 'text-align:center; vertical-align:top; '})
					item['jobtitle'] = (job_title.next).strip()
					flag_jobdiva = flag_jobdiva + 1

				if soup.find(tags[1],
				             {'style': 'padding-left: 4px; width: 220px; vertical-align:top;'}):
					location = soup.find(tags[1], {
						'style': 'padding-left: 4px; width: 220px; vertical-align:top;'})
					item['location'] = (location.next.next.next.next.next).strip()
					flag_jobdiva = flag_jobdiva + 1

				if flag_jobdiva > 1:
					item['company'] = 'jobdiva'

			elif crawl_request['spider'] == 'ziprecruter':

				if soup.find(tags[0], {'class': fields['jobtitle']}):
					item['jobtitle'] = soup.find(tags[0],
					                             {'class': fields['jobtitle']}).text.strip()
					flag_ziprecruter = flag_ziprecruter + 1

				if soup.find(tags[2], {'itemprop': fields['location']}):
					item['location'] = soup.find(tags[2],
					                             {'itemprop': fields['location']}).text.strip()
					flag_ziprecruter = flag_ziprecruter + 1

				if soup.find(tags[1], {'class': fields['company']}):
					item['company'] = soup.find(tags[1], {'class': fields['company']}).text.strip()
					flag_ziprecruter = flag_ziprecruter + 1

				if soup.find(tags[3], {'class':fields['companydes']}):
					compnydes = soup.find(tags[3], {'class':fields['companydes']})
					item['company_description']=compnydes.find('p').text.strip()
					flag_ziprecruter = flag_ziprecruter + 1

				if soup.find(tags[2], {'class':fields['jobtype']}):
					item['jobtype']=soup.find(tags[2], {'class':fields['jobtype']}).text.strip()
					flag_ziprecruter = flag_ziprecruter + 1

				if soup.find('span', {'class':'data'}):
					item['date_of_job_posted']=soup.find('span', {'class':'data'}).text.strip()
					flag_ziprecruter = flag_ziprecruter + 1

			if flag_career > 1 or flag_indeed > 1 or flag_jobdiva > 1 or flag_ziprecruter > 1:
				item['website_name'] = crawl_request['website_name']
				item['date_of_scraped']=str(datetime.datetime.utcnow())
				item['url'] = response.url
		except Exception as e:
			logger.error('parse_items|spider :%s|error : %s', crawl_request['spider'], e)
	return item


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
				if urlPattern['jobpage']=='yes':
					sel_htmls = soup.find_all(urlPattern['css-sel'],{urlPattern['tag-name']:urlPattern['extrackURLFrom']})
					for sel_html in sel_htmls:
						links.append(sel_html.a['href'])
					if crawl_request['spider']=='job_scrapper':
						pagination = soup.find('div', {'class': 'pagination'})
						links_html = pagination.find_all('a', href=True)
						for link_html in links_html:
							if link_html['href'] not in links:
								links.append(link_html['href'])
				else:
					sel_html = soup.find(urlPattern['css-sel'],{urlPattern['tag-name']:urlPattern['extrackURLFrom']})
					links_html = sel_html.find_all('a', href=True)
					for link_html in links_html:
						links.append(link_html['href'])

				return {'type': 'links', 'content': links}
			else:

				temp_crawl_request = {'fields': urlPattern['fields'], 'spider': crawl_request['spider'],
				                      'urlPattern': urlPattern['pattern'],
				                      'website_name': crawl_request['website_name']}
				item = {}
				item = parse_field(temp_crawl_request, response, response_value, tags)
				print('items::::::::::', item)
				return {'type': 'items', 'content': item}

def url_lib_request(url):
	respose = urllib.urlopen(url)
	soup = BeautifulSoup(respose)
	return soup
