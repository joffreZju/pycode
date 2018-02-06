# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import pymongo
import codecs
import datetime
from scrapy.exceptions import DropItem

class VoguePipeline(object):
    # save to mongo
    def __init__(self):
        self.con = pymongo.MongoClient('10.214.224.142',20000)
        self.db = self.con.onlineshop
        self.vogue = self.db["vogue"]
        self.update_time = datetime.datetime.utcnow()

        self.db_sina = self.con.Sina_Distributed
        self.brand = self.db_sina["brand_information"]
        self.brand_info = {}
        for i in self.brand.find({},{"brand_name":1}):
            self.brand_info[ i['brand_name'].lower() ] = i['_id']

    def process_item(self, item, spider):
        if self.brand_info.has_key( item['brand_name'].lower() ):
            item['brand_id'] = self.brand_info[ item['brand_name'].lower() ]
        item['update_time'] = self.update_time
        self.vogue.insert( dict(item) )
        return item

    
    # save to data.json
    # def __init__(self):
    #     self.file=codecs.open("data.json","wb","utf-8")

    # def process_item(self, item, spider):
    #     line = json.dumps( dict(item), ensure_ascii=False )+'\n'
    #     self.file.write(line)
    #     return item