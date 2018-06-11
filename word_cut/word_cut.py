# -*- coding: utf-8 -*-
import jieba
import pymongo
import random
jieba.load_userdict("dict.txt")

# from online_shop_spider import dbcon_parameter
brand_list = ['Chanel','Dior', 'HERMES', 'Coach', 'Furla', 'Prada', 'FENDI',
              'CLINIQUE', 'SK-II', 'OLAY', 'LANEIGE', 'Sulwhasoo', 'MCM',
              'Givenchy', 'LONGCHAMP']


class WordCut(object):

    def __init__(self):
        self.con_from = pymongo.MongoClient('10.214.224.142',20000)
        db_from = self.con_from['onlineshop']
        self.jd_from = db_from['jd']
        self.con_to = pymongo.MongoClient('10.214.224.142',20000)
        db_to = self.con_to['onlineshop']
        self.word_cut = db_to['jd_word_cut_1208']

    def get_closest_time(self):
        # results = self.jd_from.find({}).sort("update_date",pymongo.DESCENDING).limit(1)
        # for item in results:
        #     return item['update_date']
        update_date = self.jd_from.distinct("update_date")
        return sorted(list(update_date))[len(update_date)-1]

    def cut_word(self):
        # sample_num = 50
        update_time = self.get_closest_time()
        print(update_time)
        for brand in brand_list:
            results = []
            print(brand)
            items = self.jd_from.find({"brand_name": brand, "update_date": update_time, "main_type":""})
            # find all records
            for item in items:
                results.append(item)
            # get sample_num samples from records
            sample_num = 30 if len(results) >= 30 else len(results)
            samples = random.sample(results, sample_num)
            # cut the product_name and insert into db
            for sample in samples:
                item = dict()
                item['_id'] = sample['product_id']
                item['product_name'] = sample['product_name']
                gene = jieba.cut(sample['product_name'])
                item['word_cut'] = []
                for each_word in gene:
                    item['word_cut'].append(each_word)
                item['brand_name'] = sample['brand_name']
                item['product_type'] = sample['product_type']
                item['product_id'] = sample['product_id']
                self.word_cut.insert(item)
        self.con_from.close()
        self.con_to.close()

if __name__ == '__main__':
    word_cut = WordCut()
    # word_cut.cut_word()
    # print word_cut.get_closest_time()