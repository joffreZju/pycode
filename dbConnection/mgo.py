# -*- coding: utf-8 -*-

import jieba
import pymongo
import random

# conn = pymongo.MongoClient('10.214.224.142',20000)
# db = conn.onlineshop
# col = db.Copy_of_kaolaGoods

conn = pymongo.MongoClient('127.0.0.1', 27017)
db = conn.test
col = db.test
# for i in range(0,10):
#     dic = {
#         "_id":i,
#         "sqrt":i*i
#     }
#     col.insert(dic)
li = []
# for doc in col.find({"sqrt":4},{"_id":0}):
for doc in col.distinct("_id"):
    print(doc)

#     li.append(doc)

# dic = {"list":li}
# col.insert(dic)