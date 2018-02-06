# -*- coding: utf-8 -*-
import scrapy
from .. import items
from selenium import webdriver
import time
import pymongo
import codecs, json


def get_all_urls():
    con = pymongo.MongoClient('127.0.0.1', 27017)
    stock_db = con["stock"]
    stock_code_HS = stock_db["stock_code_hs"]
    stock_code_HK = stock_db["stock_code_hk"]
    stock_code_US = stock_db["stock_code_us"]
    for item in stock_code_HS.find():
        pass




class XueqiuSpider(scrapy.Spider):
    name = "xueqiu"
    # JS = True
    allowed_domains = ["eastmoney.com"]
    start_urls = [

    ]
