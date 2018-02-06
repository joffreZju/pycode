# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo

class XueqiuPipeline(object):
    # save to mongo
    def __init__(self):
        self.con = pymongo.MongoClient('127.0.0.1', 27017)
        self.stock_db = self.con["stock"]
        self.stock_info_day = self.stock_db["stock_info_day"]

    def process_item(self, item, spider):
        self.stock_info_day.insert(dict(item))
        return item
