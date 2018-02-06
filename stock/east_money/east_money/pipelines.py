# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import codecs
import json
import pymongo
import datetime
import re


class EastMoneyPipeline(object):
    # save to data.json
    # def __init__(self):
    #     self.file = codecs.open("data.json", "wb", "utf-8")
    #
    # def process_item(self, item, spider):
    #     line = json.dumps(dict(item), ensure_ascii=False) + '\n'
    #     self.file.write(line)
    #     return item

    # save to mongo
    def __init__(self):
        self.con = pymongo.MongoClient('127.0.0.1', 27017)
        self.stock_db = self.con["stock"]
        self.stock_code_HS = self.stock_db["stock_code_hs"]
        self.stock_code_HK = self.stock_db["stock_code_hk"]
        self.stock_code_US = self.stock_db["stock_code_us"]

    def process_item(self, item, spider):
        if spider.name == 'stock_code_hs_hk':
            if item['stock_exchange'] == 'HK':
                self.stock_code_HK.replace_one({'code': item['code']}, dict(item), upsert=True)
            else:
                self.stock_code_HS.replace_one({'code': item['code']}, dict(item), upsert=True)
        elif spider.name == 'stock_code_us':
            self.stock_code_US.replace_one({'code': item['code']}, dict(item), upsert=True)
        return item
