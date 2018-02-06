# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

# import scrapy
from scrapy.item import Item,Field


class CsdnblogcrawlItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # pass
    blog_name = Field()
    blog_url = Field()
