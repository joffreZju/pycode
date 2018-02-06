# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from neeuspider import items
import codecs
import json

class NeeuspiderPipeline(object):
    def __init__(self):
        # self.file = codecs.open("data2.json", "wb", "utf-8")
        self.con = pymongo.MongoClient('localhost', 27017)
        self.db = self.con.neeu2
        self.BrandInfo = self.db["brand"]
        self.BrandNews = self.db["brandnews"]

    def process_item(self, item, spider):
        # line = json.dumps(dict(item), ensure_ascii=False) + '\n'
        # self.file.write(line)
        if(isinstance(item, items.BrandItem)):
            # 品牌信息
            # print(item)
            self.BrandInfo.insert(dict(item))
        elif(isinstance(item, items.NewsItem)):
            # 各个品牌的新闻
            self.BrandNews.insert(dict(item))

        return item

    def __del__(self):
        self.con.close()