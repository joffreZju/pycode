# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class KaolaItem(scrapy.Item):
    # define the fields for your item here like:
    product_name = scrapy.Field()
    product_id = scrapy.Field()
    brand_name = scrapy.Field()
    brand_id = scrapy.Field()
    product_type = scrapy.Field()
    people_aimed = scrapy.Field()
    comment_num = scrapy.Field()
    price = scrapy.Field()
    market_price = scrapy.Field()
    rank = scrapy.Field()
    data_sourse = scrapy.Field()
    update_time = scrapy.Field()
