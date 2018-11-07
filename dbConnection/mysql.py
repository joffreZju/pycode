# -*- coding: utf-8 -*-

import pymysql
import pymongo

conn_sql = pymysql.connect(host='10.214.224.116',
                           port=3306,
                           user='root',
                           password='database',
                           db='news_dataset',
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)

conn_mgo = pymongo.MongoClient('10.214.224.142', 20000)
col = conn_mgo['finance_news']['corpus']

cursor = conn_sql.cursor()
# sql = "insert into alldata (website, url) values (%s, %s)"
# cursor.execute(sql, ('1', '1'))
# conn.commit()

sql = """select count(*) as count from alldata"""
cursor.execute(sql)
count = cursor.fetchone()['count']

sql = """select website, url, crawltime, company, title, content, abstract, datetime, original, author
        from alldata limit %s, %s;"""

skip, limit = 0, 1000
while skip < count:
    cursor.execute(sql, (skip, limit))
    data = cursor.fetchall()
    skip += len(data)
    col.insert_many(data)
