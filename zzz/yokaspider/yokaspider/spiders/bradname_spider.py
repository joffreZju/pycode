# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy import Selector
from scrapy import Request
from yokaspider.items import BrandUrl
from yokaspider import tools
from yokaspider.pagetype import newspage_type
from yokaspider.tools import URL_NO_FILTER
import logging
import re

class YokaNewsSpider(Spider):
    name = 'yoka_brand_spider'
    start_urls = ['http://brand.yoka.com/brandlist.htm']

    def __init__(self):
        super(YokaNewsSpider, self).__init__()
        self.backupCharset = 'gb18030'

    # 抓取品牌列表页面上的品牌链接
    def parse(self, response):
        self.response_body_decode(response)
        sel = Selector(response)
        # 获取所有的品牌链接
        homeurl = tools.getHomeUrl(response.url)
        brandlist = sel.xpath('//div[@class="mask"]//ul//li//a//@href').extract()
        brandlist.extend(sel.xpath('//div[@class="imgShow"]/dl/dt/a/@href').extract())
        print len(brandlist)
        for brand in brandlist:
            url = homeurl + brand
            yield Request(url, callback=self.parseMainPage)

    # 解析品牌主页面上
    def parseMainPage(self, response):
        self.response_body_decode(response)
        sel = Selector(response)
        homeurl = tools.getHomeUrl(response.url)
        # 提取品牌英文名和中文名
        names = sel.xpath('//div[@class="brandProfile"]/dl[@class="profile clearfix"]\
        /dd[@class="detail"]//a//text()').extract()
        # 上部所有链接
        all_links = sel.xpath('//div[@class="m-nav mb0"]//a//@href').extract()
        newsMore = all_links[5]
        if len(names) == 2:
            chn_name = names[0]
            eng_name = names[1]
        elif len(names) == 1:
            chn_name = eng_name = names[0]
        else:
            branditem = BrandUrl()
            branditem['url'] = response.url
            branditem['code'] = response.headers['code']
            yield branditem

     # 检测response.body的编码，并转换成Unicode

    def response_body_decode(self, response):
        charset = tools.detectPageCharset(response.body)
        if charset is not None:
            try:
                response.body.decode(charset)
            except UnicodeDecodeError:
                response.body.decode(self.backupCharset)
        else:
            logging.log(logging.WARNING, "Can not detect the charset encoding of " + response.url)