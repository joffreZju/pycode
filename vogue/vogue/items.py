# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class VogueItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    about = scrapy.Field()
    brand_id = scrapy.Field()
    brand_name = scrapy.Field()
    cn_brand_name = scrapy.Field()
    products = scrapy.Field()
    story = scrapy.Field()
    history = scrapy.Field()
    update_time = scrapy.Field()
