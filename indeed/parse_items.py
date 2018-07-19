import datetime
import os
import re
import urllib

import scrapy
from bs4 import BeautifulSoup
from pygrok import Grok
from scrapy.utils.log import logger


def parse_links(crawl_request, response, response_value):
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
							if crawl_request['spider'] == 'Dice1' or crawl_request['spider'] == 'Dice':
								if soup.find('link', {'rel': 'next'}):
									links.append(soup.find('link', {'rel': 'next'})['href']
)
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

				temp_crawl_request = {'spider': crawl_request['spider'],
				                      'urlPattern': urlPattern['pattern'],
				                      'website_name': crawl_request['website_name'],
				                      }
				item = {}
				item = parse_fields(temp_crawl_request, response, response_value)
				print('items::::::::::', item)
				return {'type': 'items', 'content': item}


def url_lib_request(url):
	respose = urllib.urlopen(url)
	soup = BeautifulSoup(respose)
	return soup


def parse_fields(crawl_request, response, response_value):
	for url_pattern in crawl_request['urlPattern']:
		response_value = str(response.url).find(url_pattern)

		if response_value >= 0:
			break
	if response_value >= 0:
		response_html = response.text
		flag_status = 0
		soup = BeautifulSoup(response_html, "html.parser")
		if crawl_request['spider'] == 'Dice1' or crawl_request['spider'] == 'Dice':
			parsedJSON = dice_feild_parse(soup)
			parsedJSON['website_name']='Dice'
			flag_status = 1
		elif crawl_request['spider'] == 'ziprecruter':
			parsedJSON = ziprecruter_description_parse(soup)
			parsedJSON['website_name'] = 'Ziprecruter'
			flag_status = 1

		elif crawl_request['spider'] == 'job_scrapper':
			parsedJSON = indeed_field_parse(soup)
			parsedJSON['website_name'] = 'Indeed'
			flag_status = 1

		elif crawl_request['spider'] == 'sitemapspider':
			parsedJSON = careerbuider_field_parse(soup)
			parsedJSON['website_name'] = 'Careerbuilder'
			print('hai')
			flag_status = 1

		if flag_status == 1:
			parsedJSON['date_of_scraped'] = str(datetime.datetime.utcnow())
			parsedJSON['url'] = response.url
			parsedJSON['page_html'] = str(response.text)
			return parsedJSON


def ziprecruter_description_parse(soup):

	patterns = {
		"postedDate": Grok("Posted date:")
	}

	title = soup.find_all('h1', class_='job_title')
	company = soup.find_all('span', class_='hiring_company_text t_company_name')
	location = soup.find_all('span', itemprop='address')
	compensation = soup.find_all('span', class_='t_compensation')
	employmentType = soup.find_all('span', class_='t_employment_type')

	parsedJSON = {}
	parsedJSON["title"] = title[0].get_text().strip() if title else None
	parsedJSON["company"] = company[0].get_text().strip() if company else None
	parsedJSON["location"] = location[0].get_text().strip() if location else None
	parsedJSON["salary"] = compensation[0].get_text().strip() if compensation else None
	parsedJSON["employment_type"] = employmentType[0].get_text().strip() if employmentType else None

	job_divs = soup.find_all('div', class_='jobDescriptionSection')
	if job_divs:
		for div in job_divs:
			ptags = ""
			ptag = div.select('div p')
			for p in ptag:
				ptags = ptags + p.get_text()
			parsedJSON["job_description"] = ptags

	job_more = (soup.find_all('p', class_='job_more'))
	posted = job_more[1].find_all('span', class_='data')
	parsedJSON["posted"] = posted[0].get_text().strip() if posted else None

	return parsedJSON



def dice_feild_parse(soup):

	title = soup.find_all('h1', class_='jobTitle')
	#url = soup.select("link[rel=canonical]")
	company = soup.find_all('span', itemprop="name")
	location = soup.find_all('li', class_='location', itemprop="joblocation")
	skills = soup.find_all('div', class_="iconsiblings")
	employmentType = soup.select("input#empTypeSSDL")
	posted = soup.find_all('li', class_="posted hidden-xs")
	jobDescription = soup.find_all('div', itemprop="description")

	parsedJSON = {}
	parsedJSON["jobtitle"] = title[0].get_text().strip() if title else None
	#parsedJSON["url"] = url[0].get('href') if url else None
	parsedJSON["company"] = company[0].get_text().strip() if company else None
	parsedJSON["location"] = location[0].get_text().strip() if location else None
	# parsedJSON["skills"] = skills[0].get_text().strip() if skills else None
	parsedJSON["employment_type"] = employmentType[0].get('value') if employmentType else None
	parsedJSON["posted"] = posted[0].get_text().strip() if posted else None
	parsedJSON["job_description"] = jobDescription[0].get_text().strip() if posted else None
	parsedJSON["website_name"] = "Dice"

	return parsedJSON

def indeed_field_parse(soup):

	patterns = {
		"salary": Grok("Salary: %{DATA:fromAmount} to %{DATA:toAmount}/%{WORD:granularity}"),
		"salary": Grok("Salary: %{GREEDYDATA:salary}"),
		"jobType": Grok("Job Type: %{NOTSPACE:jobType}"),
		"employmentType": Grok("Employment Type : %{NOTSPACE:employmentType}")
	}

	title = soup.find_all('b', class_='jobtitle')
	company = soup.find_all('span', class_='company')
	location = soup.find_all('span', class_='location')
	posted = soup.find_all('span', class_='date')

	### Common field parsing

	parsedJSON = {}
	parsedJSON["title"] = title[0].get_text() if title else None
	parsedJSON["company"] = company[0].get_text() if company else None
	parsedJSON["location"] = location[0].get_text() if location else None
	parsedJSON["posted"] = posted[0].get_text() if posted else None

	### Parsing Salary and Employment type

	parsedJSON["salary"] = None
	parsedJSON["employment_type"] = None
	job_summary = soup.select('span#job_summary p')

	if job_summary:
		for p in job_summary:
			for pattern in patterns:
				matched = patterns[pattern].match(p.get_text())
				if matched is not None:
					for key in matched.keys():
						parsedJSON[key] = matched[key]

	salaryType = soup.find_all('span', class_='no-wrap')
	if parsedJSON["salary"] is None:
		parsedJSON["salary"] = salaryType[0].get_text().strip().replace(" -", "") if salaryType else None
	if parsedJSON["employment_type"] is None:
		parsedJSON["employment_type"] = salaryType[1].get_text().strip() if salaryType else None

	# Parsing Job Description

	### Case1
	job_description = ""
	job_description = soup.select('span#job_summary > p')
	if job_description:
		job_description[0].get_text()
		parsedJSON["job_description"] = job_description[0].get_text().strip()


	### Case 2
	job_description_ptag = soup.select('span#job_summary > p')
	job_description_div = soup.select('span#job_summary div')
	if job_description_ptag and job_description_div:
		job_description = job_description_ptag[0].get_text() + job_description_div[0].get_text()
		parsedJSON["job_description"] = job_description

	### Case3
	job_description = soup.find_all('span', class_='summary')
	if job_description:
		job_description_br = job_description[0].find_all('br')
		if job_description_br:
			parsedJSON["job_description"] = job_description_br[0].get_text()


	return parsedJSON

def careerbuider_field_parse(soup):

	title_company_data = soup.find_all('h1', class_='h3 pb col big no-mb')
	employment_type = soup.find_all('div', class_='fl-l fl-n-mobile')
	location = soup.find_all('div', class_='fl-r fl-n-mobile')

	parsedJSON = {}
	parsedJSON["title"] = title_company_data[0].get_text().split('posted by')[0] if title_company_data else None
	parsedJSON["company"] = title_company_data[0].get_text().split('posted by')[
		1].strip() if title_company_data else None
	parsedJSON["employment_type"] = employment_type[0].get_text() if employment_type else None
	parsedJSON["location"] = location[0].get_text() if location else None

	#print(soup.find_all('div', class_='fl-r fl-n-mobile')[1].get_text())

	job_description = ""
	for descp in soup.select('div#job-description ul'):
		job_description = job_description + descp.get_text().strip() + '.'

	if job_description == "":
		for descp in soup.select('div#job-description'):
			job_description = job_description + descp.get_text() + '.'

	parsedJSON["job_description"] = job_description

	return parsedJSON



