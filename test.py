import requests
from bs4 import BeautifulSoup

from scrapy_redis.spiders import RedisSpider

url = 'https://www.indeed.co.in/cmp/GRPOS.INDRT/jobs/Interview-Govt-Office-Metro-Admin-10c43fca25ab6dff?q=Government&vjs=3'
html = requests.get(url)
soup = BeautifulSoup(html.text, "html.parser")
#table_tag = soup.find('table', {'id': 'job-content'})
#table_tag = soup.find('table', {'id': 'job-content'})
company = 'location'
for item in soup.find('span',{'class':company}):
	print(item)
jobtitle = 'jobtitle'
for item1 in soup.find('b',{'class':jobtitle}):
	print(item1.get_text())