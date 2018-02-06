# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NeeuspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class NewsItem(scrapy.Item):
    title = scrapy.Field()              #新闻标题
    date = scrapy.Field()               #发布日期
    brandname = scrapy.Field()          #品牌名称（英文）
    content = scrapy.Field()            #新闻内容

class BrandItem(scrapy.Item):
    news_href = scrapy.Field()         #品牌ID
    eng_name = scrapy.Field()   #品牌英文名
    chn_name = scrapy.Field()   #品牌中文名
