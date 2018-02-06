# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy import Selector
from scrapy.spiders import Rule
from hwspider import items
from scrapy import Request
# from selenium import webdriver
import json

#http://search.jd.com/Search?keyword=%E6%B5%B7%E5%A4%96%E8%B4%AD&enc=utf-8&page=3

class HWSpider(CrawlSpider):
    name = 'haiwaigou'
    #allow_domains = ['http://jd.com/']
    # start_urls = ['https://search.jd.com/Search?keyword="海外购"&enc=utf-8&page=' + str(2*n-1)
    #               for n in range(1,101)]
    start_urls = ['https://search.jd.com/Search?keyword="海外购"&enc=utf-8&page=1']
    rules = (
        Rule(LxmlLinkExtractor(allow=(r'http://search\.jd\.com/Search\?keyword="海外购"&enc=utf-8&page=\d+')), follow=True),
    )

    def parse(self, response):
        sel = Selector(response)
        goods = sel.xpath('//ul[@class="gl-warp clearfix"]//li')
        for good in goods:
            item = items.GoodDetailItem()
            item['id'] = good.xpath('./@data-sku')[0].extract()
            item['price'] = good.xpath('.//div[@class="p-price"]/strong/@data-price').extract()
            item['name'] = good.xpath('.//div[@class="p-name p-name-type-2"]/a/em/text()').extract()
            evaluationUrl = 'http://club.jd.com/clubservice.aspx?method=GetCommentsCount&referenceIds=' + item.get('id')
            r = Request(evaluationUrl, callback=self.parse_evaluation)
            r.meta['item'] = item
            yield r 

    def parse_evaluation(self, response):
        eva_s = json.loads(response.body)
        # print eva_s+"***********"
        item = response.meta['item']
        item['score1count'] = eva_s['CommentsCount'][0]['Score1Count']
        item['score2count'] = eva_s['CommentsCount'][0]['Score2Count']
        item['score3count'] = eva_s['CommentsCount'][0]['Score3Count']
        item['score4count'] = eva_s['CommentsCount'][0]['Score4Count']
        item['score5count'] = eva_s['CommentsCount'][0]['Score5Count']
        item['commentcount'] = eva_s['CommentsCount'][0]['CommentCount']
        item['goodcount'] = eva_s['CommentsCount'][0]['GoodCount']
        item['generalcount'] = eva_s['CommentsCount'][0]['GeneralCount']
        item['poorcount'] = eva_s['CommentsCount'][0]['PoorCount']
        return item