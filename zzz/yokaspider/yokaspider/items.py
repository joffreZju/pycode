# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class YokaspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

# 品牌英文名和中文名
class BrandItem(scrapy.Item):
    eng_name = scrapy.Field()
    chn_name = scrapy.Field()
    url = scrapy.Field()

class BrandUrl(scrapy.Item):
    url = scrapy.Field()
    code = scrapy.Field()


# 保存品牌新闻
class NewsItem(scrapy.Item):
    title = scrapy.Field()       # 新闻标题
    date = scrapy.Field()        # 发布日期
    brandname = scrapy.Field()   # 品牌名称（英文）
    content = scrapy.Field()     # 新闻内容