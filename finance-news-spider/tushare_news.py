# -*- coding: utf-8 -*-

import tushare as ts
import pandas
import pymongo
import datetime
import time

conn = pymongo.MongoClient('10.214.224.142', 20000)
db = conn['finance_news']


def get_latest_news():
    col = db['sina_finance']

    df = ts.get_latest_news(show_content=True)

    for _, row in df.iterrows():
        if row['content'] is None:
            continue
        col.replace_one(
            {
                'url': row['url'],
            },
            {
                'classify': row['classify'],
                'title': row['title'],
                'time': row['time'],
                'year': 2018,
                'url': row['url'],
                'content': [c.strip() for c in row['content'].split('\n') if len(c.strip()) > 0],
                'crawl_time': datetime.datetime.fromtimestamp(time.time()),
            }, upsert=True
        )


if __name__ == '__main__':
    while True:
        try:
            get_latest_news()
            print(datetime.datetime.fromtimestamp(time.time()), '完成一次爬取')
        except Exception as e:
            print(str(e))
        time.sleep(30 * 60)
