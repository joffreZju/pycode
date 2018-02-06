# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy import Request
from scrapy import Selector
from neeuspider.items import NewsItem
from neeuspider.globalVariants import DBUrl
import pymongo

class NewsSpider(Spider):
    name = "newsspider"
    start_urls = ['http://www.neeu.com/brand/home.html']

    def __init__(self):
        super(NewsSpider, self).__init__()
        self.homeurl = 'http://www.neeu.com'
        self.nextpagetext = '下一页'
    #     con = pymongo.MongoClient(DBUrl.HOST, DBUrl.PORT)
    #     db = con['neeu']
    #     brand = db['brand']
    #     self.brandUrl = {} #保存href到url的映射
    #     for each_brand in brand.find({}, {"news_href" : 1, "eng_name":1}):
    #         self.start_urls.append(each_brand["eng_name"])
    #         self.brandurl[each_brand["news_href"]] = each_brand["eng_name"]

    #获得各个品牌新闻主页面的链接
    def parse(self, response):
        bpress_url = 'http://www.neeu.com/brand/press.jsp'
        response.body.decode("gbk")
        sel = Selector(response)
        brands = sel.xpath('//div[@class="brandname"]/ul//li')
        for brand in brands:
            # 得到品牌的英文名
            eng_name = brand.xpath('./h4/a[@href]/text()')[0].extract()
            # 将提取到的品牌URL替换为该品牌资讯所在的URL:bpress_url
            news_href = brand.xpath('./h4/a[@href]/@href')[0].extract().replace("/brand", bpress_url)
            #生成新的Request
            r = Request(news_href, callback=self.parseNewsList)
            r.meta['brandname'] = eng_name
            r.meta['findAllList'] = True
            yield r

    # 解析品牌当前新闻列表页面下的所有新闻链接
    # 以及下一页新闻列表页面链接
    def parseNewsList(self, response):
        response.body.decode("gbk")
        brandname = response.meta['brandname']
        sel = Selector(response)
        # 得到当前页面的每个新闻链接
        newslist = sel.xpath('//div[@class="brandhomenews"]/h3/a/@href').extract()
        for each_news in newslist:
            url = each_news
            r = Request(self.homeurl + url, callback=self.parseEachNews)
            r.meta['brandname'] = brandname
            yield r
        # 判断是否有需要获得当前品牌剩余新闻列表页面的链接
        # 仅在第一次访问品牌新闻页面第一页时需要
        if(response.meta['findAllList']):
            all_a = sel.xpath('//div[@class="pagesizebottom"]/a[last()-1]/text()').extract()
            max_pageno = 1  #之前为2，some brand's news may have only one page
            if(len(all_a) > 0):
                max_pageno = int(all_a[0])
                print max_pageno
            for pageno in range(2, max_pageno+1):
                # 得到下一页的链接
                nextpage = response.url + '&pageNumber=' + str(pageno)
                r = Request(nextpage, callback=self.parseNewsList)
                r.meta['brandname'] = brandname
                r.meta['findAllList'] = False   #设置为False
                # print ("BBBBBBBBBBBfind the next page url")
                # print nextpage
                yield r

    def parseEachNews(self, response):
        response.body.decode("gbk")
        sel = Selector(response)
        brandname = response.meta['brandname']
        title = sel.xpath('//div[@class="articlehead"]/h1/text()')[0].extract()
        #获得日期 url example:http://www.neeu.com/news/2016-09-23/67392.html
        date = response.url[25:35]
        paragraphs = sel.xpath('//div[@class="content"]//p/text()').extract()
        content = "".join(paragraphs)
        item = NewsItem()
        item['title'] = title
        item['date'] = date
        item['brandname'] = brandname
        item['content'] = content
        yield item


