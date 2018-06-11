# -*- coding: utf-8 -*-

import json
import csv
from collections import defaultdict
import time

"""
1. yelp数据集是json文件，并不是一个json list, 而且文件较大，无法直接打开编辑，需要使用 sed 命令先将文件处理为一个json list, 格式就是 ./*.json 所示。
执行 ./sed.sh business.json
就会将原有的 business.json 转化为 json list, 直接在原文件上修改 

2. 下面 python 脚本将yelp数据集的json格式处理为可以直接导入neo4j的csv

"""


def handle_business():
    f = open('business.json')
    data = json.load(f)
    print(type(data))
    f.close()

    business = csv.writer(open('business.csv', 'w', newline=''))
    business.writerow(['id:ID(Business)', 'name', 'neighborhood', 'city', 'state',
                       'latitude', 'longitude', 'stars', 'review_count', 'is_open'])

    category = csv.writer(open('category.csv', 'w', newline=''))
    category.writerow(['id:ID(Category)'])

    business_category = csv.writer(open('business_IN_CATEGORY_category.csv', 'w', newline=''))
    business_category.writerow([':START_ID(Business)', ':END_ID(Category)'])

    bids = set()
    cates = set()
    for i in data:
        bid = i['business_id']
        if bid not in bids:
            business.writerow([
                bid, i['name'], i['neighborhood'], i['city'], i['state'],
                i['latitude'], i['longitude'], i['stars'], i['review_count'], i['is_open']
            ])
            bids.add(bid)

        for c in i['categories']:
            cates.add(c)
            business_category.writerow([bid, c])

    for c in cates:
        category.writerow([c])


def handle_tip():
    f = open('tip.json')
    data = json.load(f)
    f.close()
    print(type(data))

    cw = csv.writer(open('user_TIP_business.csv', "w", newline=''))
    cw.writerow([':START_ID(User)', 'date', 'likes', ':END_ID(Business)'])

    for i in data:
        cw.writerow([i['user_id'], i['date'], i['likes'], i['business_id']])


def handle_user():
    f = open('user.json')
    data = json.load(f)
    print(type(data))
    f.close()

    user = csv.writer(open('user.csv', 'w', newline=''))
    user.writerow(['id:ID(User)', 'name', 'review_count', 'yelping_since',
                   'useful', 'funny', 'cool', 'fans', 'elite', 'average_stars',
                   'compliment_hot', 'compliment_more', 'compliment_profile', 'compliment_cute',
                   'compliment_list', 'compliment_note', 'compliment_plain', 'compliment_cool',
                   'compliment_funny', 'compliment_writer', 'compliment_photos'])

    user_friend_user = csv.writer(open('user_FRIEND_user.csv', 'w', newline=''))
    user_friend_user.writerow([':START_ID(User)', ':END_ID(User)'])

    dic = defaultdict(lambda: defaultdict(lambda: False))
    uids = set()
    for i in data:
        uid = i['user_id']
        if uid not in uids:
            user.writerow([
                i['user_id'], i['name'], i['review_count'], i['yelping_since'],
                i['useful'], i['funny'], i['cool'], i['fans'], i['elite'], i['average_stars'],
                i['compliment_hot'], i['compliment_more'], i['compliment_profile'], i['compliment_cute'],
                i['compliment_list'], i['compliment_note'], i['compliment_plain'], i['compliment_cool'],
                i['compliment_funny'], i['compliment_writer'], i['compliment_photos']
            ])
            uids.add(uid)

        for fid in i['friends']:
            if dic[uid][fid] is False and dic[fid][uid] is False:
                user_friend_user.writerow([uid, fid])
                user_friend_user.writerow([fid, uid])
            dic[uid][fid] = True
            dic[fid][uid] = True


def handle_review():
    f = open('review.json')
    data = json.load(f)
    print(type(data))
    f.close()

    review = csv.writer(open('review.csv', "w", newline=''))
    review.writerow(['id:ID(Review)', 'stars', 'date', 'useful', 'funny', 'cool'])

    user_write_review = csv.writer(open('user_WROTE_review.csv', "w", newline=''))
    user_write_review.writerow([':START_ID(User)', ':END_ID(Review)'])

    review_reviews_business = csv.writer(open('review_REVIEWS_business.csv', "w", newline=''))
    review_reviews_business.writerow([':START_ID(Review)', ':END_ID(Business)'])

    rids = set()
    for i in data:
        rid = i['review_id']
        if rid not in rids:
            review.writerow([
                rid, i['stars'], i['date'], i['useful'], i['funny'], i['cool']
            ])
        rids.add(rid)

        user_write_review.writerow([i['user_id'], i['review_id']])
        review_reviews_business.writerow([i['review_id'], i['business_id']])


if __name__ == '__main__':
    start = time.time()
    handle_tip()
    handle_user()
    handle_business()
    handle_review()

    print(time.time() - start)
