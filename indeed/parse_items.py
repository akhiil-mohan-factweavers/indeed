import os

from bs4 import BeautifulSoup
from scrapy.utils.log import  logger


def parse_field(crawl_request, response, response_value, tags):
	item = {}
	fields = crawl_request.get('fields',None)
	soup = BeautifulSoup(response.text, "html.parser")
	for url_pattern in crawl_request['urlPattern']:
		response_value = str(response.url).find(url_pattern)

		if response_value >= 0:
			break
	if response_value >= 0:
		try:
			print(crawl_request)
			flag_indeed = 0
			flag_career = 0
			flag_jobdiva = 0
			flag_ziprecruter = 0
			if crawl_request['spider'] == 'job_scrapper':
				if soup.find(tags[0], {'class': fields['company']}):
					item['company'] = soup.find(tags[0], {'class': fields['company']}).text
					flag_indeed=flag_indeed+1


				if soup.find(tags[1], {'class': fields['jobtitle']}):
					item['jobtitle'] = soup.find(tags[1], {'class': fields['jobtitle']}).text
					flag_indeed = flag_indeed + 1


				if soup.find(tags[0], {'class': fields['location']}):
					item['location'] = soup.find(tags[0], {'class': fields['location']}).text
					flag_indeed = flag_indeed + 1


				if soup.find(tags[0], {'class': fields['salary']}):
					item['salary'] = soup.find(tags[0], {'class': fields['salary']}).text.strip()
					flag_indeed = flag_indeed + 1


			elif crawl_request['spider'] == 'sitemapspider':

				if soup.find(tags[2], {'class': fields['company']}):
					company = soup.find(tags[2], {'class': fields['company']}).text.strip()
					item['company'] = company.split("posted by ",1)[1]
					flag_career =flag_career+1


				if soup.find(tags[0], {'class': fields['jobtitle']}):
					job_title = soup.find(tags[0], {'class': fields['jobtitle']}).text.strip()
					item['jobtitle'] = job_title.split("\n", 1)[0]
					flag_career = flag_career + 1


				if soup.find(tags[1], {'class': fields['location']}):
					item['location'] = soup.find(tags[1], {'class': fields['location']}).text.strip()
					flag_career = flag_career + 1

			elif crawl_request['spider'] == 'jobdiva':

				if soup.find(tags[0], {'style':'text-align:center; vertical-align:top; '}) :
					job_title = soup.find(tags[0], {'style':'text-align:center; vertical-align:top; '})
					item['jobtitle']= (job_title.next).strip()
					flag_jobdiva= flag_jobdiva+1

				if soup.find(tags[1], {'style':'padding-left: 4px; width: 220px; vertical-align:top;'}) :
					location = soup.find(tags[1], {'style':'padding-left: 4px; width: 220px; vertical-align:top;'})
					item['location'] = (location.next.next.next.next.next).strip()
					flag_jobdiva = flag_jobdiva + 1

				if flag_jobdiva>1:
					item['company'] = 'jobdiva'

			elif crawl_request['spider'] == 'ziprecruter':

				if soup.find(tags[0], {'class':fields['jobtitle']}) :
					item['jobtitle'] = soup.find(tags[0], {'class':fields['jobtitle']}).text.strip()
					flag_ziprecruter= flag_ziprecruter+1

				if soup.find(tags[2], {'itemprop':fields['location']}) :
					item['location'] = soup.find(tags[2], {'itemprop':fields['location']}).text.strip()
					flag_ziprecruter = flag_ziprecruter + 1

				if soup.find(tags[1], {'class': fields['company']}):
					item['company'] = soup.find(tags[1], {'class': fields['company']}).text.strip()
					flag_ziprecruter = flag_ziprecruter + 1

			if flag_career > 1 or flag_indeed > 1 or flag_jobdiva >1 or flag_ziprecruter >1:
				item['website_name'] = crawl_request['website_name']
				item['url'] = response.url
		except Exception as e:
			logger.error('parse_items|spider :%s|error : %s',crawl_request['spider'],e)
	return item

def parse_links(crawl_request, response, response_value, tags):
	links = []
	urlPatterns = crawl_request.get('urlPattern', None)
	match_value=-2
	soup = BeautifulSoup(response.text, "html.parser")
	for urlPattern in urlPatterns:
		print(urlPattern)
		for pattern in urlPattern.get('pattern',None):
			match_value = str(response.url).find(pattern)
			print(match_value)
			if pattern =='https://www.indeed.co.in/browsejobs':
				if pattern == str(response.url):
					match_value=0
				else:
					match_value =-2
			if match_value >= 0:
				break
		if match_value>=0:
			if urlPattern['followOnly'] =='true':
				sel_html = soup.find(id=urlPattern['extrackURLFrom'])
				links_html = sel_html.find_all('a',href =True)
				for link_html in links_html:
					links.append(link_html['href'])
				return {'type':'links','content': links}
			else:
				print(urlPatterns)
				print(crawl_request['spider'])
				temp_crawl_request = {'fields': urlPattern['fields'],'spider': crawl_request['spider'],'urlPattern':urlPattern['pattern'],'website_name': crawl_request['website_name']}
				item = {}
				item = parse_field(temp_crawl_request, response, response_value, tags)
				print('items::::::::::',item)
				return {'type':'items','content': item}





