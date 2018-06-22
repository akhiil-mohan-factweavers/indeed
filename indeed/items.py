# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class IndeedItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    title = scrapy.Field()
    h1_tag = scrapy.Field()
    h2_tag = scrapy.Field()
    p_tag = scrapy.Field()
    status = scrapy.Field()
    links = scrapy.Field()

    #items = scrapy.Field()