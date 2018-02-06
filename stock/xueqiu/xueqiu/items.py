# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class XueqiuItem(scrapy.Item):
    # define the fields for your item here like:
    date = scrapy.Field()
    name = scrapy.Field()
    code = scrapy.Field()
    stock_exchange = scrapy.Field()
    open = scrapy.Field()
    pre_close = scrapy.Field()
    low = scrapy.Field()
    high = scrapy.Field()
    volume = scrapy.Field()
    amount = scrapy.Field()
    marketcap = scrapy.Field()
    capitalization = scrapy.Field()
    pass
