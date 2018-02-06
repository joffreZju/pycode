# -*- coding: utf-8 -*-

import pymongo
from yokaspider.items import BrandItem,NewsItem,BrandUrl
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class YokaspiderPipeline(object):
    def __init__(self):
        con = pymongo.MongoClient('localhost', 27017)
        db = con.yoka2
        self.BrandInfo = db['brandinfo']
        self.BrandNews = db['brandnews']
        self.BrandUrl = db['brandurl']

    def process_item(self, item, spider):
        if isinstance(item, NewsItem):
            self.BrandNews.insert(dict(item))
        elif isinstance(item, BrandItem):
            self.BrandInfo.insert(dict(item))
        elif isinstance(item, BrandUrl):
            self.BrandUrl.insert(dict(item))
        return item
