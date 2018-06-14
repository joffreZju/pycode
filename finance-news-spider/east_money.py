# -*- coding: utf-8 -*-

import time
import datetime
import pymongo
import requests
from lxml import etree

conn = pymongo.MongoClient('10.214.224.142', 20000)
db = conn['finance_news']


def get_list_pages(base_url: str):
    print('\n-------------开始爬取', base_url, '的新闻列表链接------------\n')

    col = db['em_news_start_urls']
    resp = requests.get(base_url)
    if resp.status_code != 200:
        return

    a_tabs = etree.HTML(resp.text).xpath('//div[@class="mainMenu"]/div/a')
    for i in a_tabs:
        text, href = i.xpath('./text()')[0], i.xpath('./@href')[0]
        if href.find('/news/') == -1:
            continue
        if href.find('.eastmoney.com') == -1:
            href = base_url + href

        print(text, href)
        col.replace_one(
            {
                'url': href
            },
            {
                'url': href,
                'classify': text,
            }, upsert=True
        )


if __name__ == '__main__':
    urls = ['http://finance.eastmoney.com/',
            'http://stock.eastmoney.com/',
            'http://quote.eastmoney.com/',
            'http://data.eastmoney.com/center/',
            'http://option.eastmoney.com/',
            'http://global.eastmoney.com/',
            'http://hk.eastmoney.com/',
            'http://forex.eastmoney.com/',
            'http://futures.eastmoney.com/',
            'http://gold.eastmoney.com/',
            "http://fund.eastmoney.com/fund.html",
            'http://fund.eastmoney.com/fundguzhi.html',
            'http://fund.eastmoney.com/data/fundranking.html',
            'http://xinsanban.eastmoney.com/',
            'http://money.eastmoney.com/',
            'http://bank.eastmoney.com/',
            'http://bond.eastmoney.com/',
            'http://insurance.eastmoney.com/',
            'http://trust.eastmoney.com/',
            'http://stock.eastmoney.com/gegu.html',
            'http://finance.eastmoney.com/company.html',
            'http://biz.eastmoney.com/',
            'http://enterprise.eastmoney.com/',
            'http://finance.eastmoney.com/news/ccjxw.html',
            'http://renwu.eastmoney.com/',
            'http://media.eastmoney.com/',
            'http://guba.eastmoney.com/',
            'http://jijinba.eastmoney.com/',
            'http://blog.eastmoney.com/',
            'http://group.eastmoney.com/index.html',
            'http://vote.eastmoney.com/index.html',
            'http://jigou.eastmoney.com/',
            'http://mingjia.eastmoney.com/',
            'http://acttg.eastmoney.com/pub/web_nr_dcsy_sylm_01_01_01_0',
            'http://auto.eastmoney.com/',
            'http://caipiao.eastmoney.com/',
            'http://so.eastmoney.com/']

    # get_list_pages('http://bond.eastmoney.com/news/czqxw.html')
    # get_list_pages('http://bank.eastmoney.com/news/cyhdd_24.html')
    for u in urls:
        get_list_pages(u)
        time.sleep(3)
