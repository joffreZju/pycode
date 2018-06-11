# -*- coding:utf-8 -*-
import os
import json
import jieba
import pymongo

# from online_shop_spider import dbcon_parameter

# brand_list = ['Chanel','Dior', 'HERMES', 'Coach', 'Furla', 'Prada', 'FENDI',
#               'CLINIQUE', 'SK-II', 'OLAY', 'LANEIGE', 'Sulwhasoo', 'MCM',
#               'Givenchy', 'LONGCHAMP']
# brand_list = set(['SK-II', 'OLAY', 'LANEIGE', 'Sulwhasoo', 'MCM', 'Givenchy', 'LONGCHAMP'])


class TypeTagAdder(object):

    def __init__(self, db_host, db_port, db_name, col_name, map_file_path='map.json', word_dict_path='dict.txt'):
        self.con = pymongo.MongoClient(db_host, db_port)
        self.db = self.con[db_name]
        self.jd = self.db[col_name]
        self.file_path = map_file_path
        jieba.load_userdict(word_dict_path)

    def get_map_table(self):
        if not os.path.isfile(self.file_path):
            raise ValueError('A valid file path is required!')
        with open(self.file_path) as map_f:
            data = json.load(map_f)
        result = dict()
        for brand in data.keys():
            result[brand] = dict()
            for item in data[brand]:
                for key_word in item['key_words']:
                    result[brand][key_word] = dict()
                    result[brand][key_word]['main_type'] = item['main_type']
                    result[brand][key_word]['sub_type'] = item['sub_type']
        return result

    def get_latest_time(self):
        # 得到数据库中最新数据的更新时间
        # results = self.jd.find({}).sort("update_date", pymongo.DESCENDING).limit(1)
        # for item in results:
        #     return item['update_date']
        update_date = self.jd.distinct("update_date")
        return sorted(list(update_date))[len(update_date)-1]

    def get_product_type(self, product_name, brand_name, map_table):
        words = jieba.cut(product_name)
        # record_dict记录该商品名对应的商品类型结果,最终选取count值最大的key对应的结果
        # record_dict:
        #       key:   main_type
        #       value: count  计数值
        #              sub_type_set: 子类型列表,用set来记录
        record_dict = dict()
        final_type_dict = dict()
        for word in words:
            if word not in map_table[brand_name].keys():
                continue
            type_info = map_table[brand_name][word]
            main_type = type_info['main_type']
            # 对于每个关键词，可以找到映射表中对应一条记录，包含主要类型，次类型
            if main_type not in record_dict.keys():
                record_dict[main_type] = {
                    'count': 0,
                    'sub_type_set': set()
                }
            record_dict[main_type]['count'] += 1
            record_dict[main_type]['sub_type_set'].add(type_info['sub_type'])
        # 选择count值最大的那条记录
        max_count = 0
        max_key = ''
        for key in record_dict.keys():
            if record_dict[key]['count'] > max_count:
                max_count = record_dict[key]['count']
                max_key = key
        final_type_dict['main_type'] = max_key
        final_type_dict['sub_type'] = list(record_dict[max_key]['sub_type_set']) if max_key else []
        return final_type_dict

    def add_type_tag(self):
        latest_time = self.get_latest_time()
        print(latest_time)
        map_table = self.get_map_table()
        for product in self.jd.find({"update_date": latest_time, "main_type":""}):
            p_name = product['product_name']
            b_name = product['brand_name']
            # if b_name not in brand_list:
            #     continue
            type_dict = self.get_product_type(p_name, b_name, map_table)
            product['main_type'] = type_dict['main_type']
            product['sub_type'] = type_dict['sub_type']
            self.jd.save(product)


if __name__ == '__main__':
    host = "10.214.224.142"
    port = 20000
    db_name = 'onlineshop'
    col_name = 'jd'
    map_file_path = 'map.json'
    word_dict_path = 'dict.txt'
    ta = TypeTagAdder(host, port, db_name, col_name, map_file_path, word_dict_path)
    ta.add_type_tag()
