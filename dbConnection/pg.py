# -*- coding:utf-8 -*-
import psycopg2

conn = psycopg2.connect(database="postgres", user="postgres", password="postgres", host="127.0.0.1", port="5432")

cur = conn.cursor()
cur.execute("SELECT * from xls")
rows = cur.fetchall()
# cursor.fetchall() 这个例程获取所有查询结果（剩余）行，返回一个列表。空行时则返回空列表。

rows = sorted(rows, key=lambda x: x[4], reverse=True)
weight = 0
volunm = 0
result = set()
for row in rows:
    if weight + row[2] <= 30 and volunm + row[3] <= 135:
        weight += row[2]
        volunm += row[3]
        result.add(int(row[0]))

# for i in result:
#     cur.execute("update xls set flag = %s where number = %s",(1,i))

print weight, volunm
print result
conn.close()
