# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GoodDetailItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    score1count = scrapy.Field()
    score2count = scrapy.Field()
    score3count = scrapy.Field()
    score4count = scrapy.Field()
    score5count = scrapy.Field()
    commentcount = scrapy.Field()
    goodcount = scrapy.Field()
    generalcount = scrapy.Field()
    poorcount = scrapy.Field()
