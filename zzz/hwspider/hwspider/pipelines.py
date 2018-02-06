# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import pymongo
import codecs

class HwspiderPipeline(object):
    def __init__(self):
        # self.file = codecs.open("data2.json", "wb", "utf-8")
        self.con = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = self.con.jd
        self.goods = self.db["goods_info"]

    def process_item(self, item, spider):
        # line = json.dumps(dict(item), ensure_ascii=False) + '\n'
        # self.file.write(line)
        self.goods.insert(dict(item))
        return item
