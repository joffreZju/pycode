# -*- coding: utf-8 -*-
import scrapy
from .. import items
import time
import codecs, json


# class StockCodeChinaSpider(scrapy.Spider):
#     name = "stock_code_china"
#     allowed_domains = ["eastmoney.com"]
#     start_urls = (
#         "http://quote.eastmoney.com/stocklist.html#sh",
#     )
#
#     def parse(self, response):
#         sel = scrapy.Selector(response)
#         sh_firm = sel.xpath('//div[@id="quotesearch"]/ul[1]/li')
#         for firm in sh_firm:
#             item = items.StockCodeItem()
#             text = ''.join(firm.xpath('./a[@target="_blank"]/text()').extract())
#             left = text.find('(')
#             right = text.find(')')
#             item['name'] = text[:left]
#             item['code'] = text[left + 1:right]
#             item['stock_exchange'] = "SH"
#             yield item
#
#         sz_firm = sel.xpath('//div[@id="quotesearch"]/ul[2]/li')
#         for firm in sz_firm:
#             item = items.StockCodeItem()
#             text = ''.join(firm.xpath('./a[@target="_blank"]/text()').extract())
#             left = text.find('(')
#             right = text.find(')')
#             item['name'] = text[:left]
#             item['code'] = text[left + 1:right]
#             item['stock_exchange'] = "SZ"
#             # yield item


class StockCodeHSHKSpider(scrapy.Spider):
    name = "stock_code_hs_hk"
    JS = True
    allowed_domains = ["eastmoney.com"]
    start_urls = [
        "http://quote.eastmoney.com/center/list.html#50_1",  # HK
        "http://quote.eastmoney.com/center/list.html#10",  # SH A
        "http://quote.eastmoney.com/center/list.html#11",  # SH B
        "http://quote.eastmoney.com/center/list.html#20",  # SZ A
        "http://quote.eastmoney.com/center/list.html#21",  # SZ B
    ]

    def parse(self, response):
        sel = scrapy.Selector(response)
        pages = sel.xpath('//div[@id="pagenav"]/a')
        index = ''
        for k, v in enumerate(pages):
            if v.xpath('./text()').extract()[0] == u'下一页':
                index = str(k)
                break
        max_page = sel.xpath('//div[@id="pagenav"]/a[' + index + ']/text()').extract()[0]

        url = response.url
        print(url, '---max_page---', max_page)

        item = items.StockCodeItem()
        if url.find('50_1') != -1:
            item['stock_exchange'] = 'HK'
        elif url.find('10') != -1 or url.find('11') != -1:
            item['stock_exchange'] = 'SH'
        elif url.find('20') != -1 or url.find('21') != -1:
            item['stock_exchange'] = 'SZ'

        for page in range(1, int(max_page) + 1):
            # for page in range(1, 2):
            request = scrapy.Request(url=url, callback=self.get_item, dont_filter=True)
            request.meta['page'] = page
            request.meta['item'] = item
            yield request

    def get_item(self, response):
        sel = scrapy.Selector(response)
        item = response.meta['item']
        hk_firm = sel.xpath('//table[@id="fixed"]/tbody/tr')
        for k, firm in enumerate(hk_firm):
            if k == 0:
                continue
            item['code'] = ''.join(firm.xpath('./td[2]/a/text()').extract())
            item['name'] = ''.join(firm.xpath('./td[3]/a/text()').extract())
            yield item


class StockCodeUSASpider(scrapy.Spider):
    name = "stock_code_us"
    JS = True
    allowed_domains = ["eastmoney.com"]
    start_urls = (
        "http://quote.eastmoney.com/center/list.html#70_2",
    )

    def parse(self, response):
        sel = scrapy.Selector(response)
        pages = sel.xpath('//div[@id="pagenav"]/a')
        index = ''
        for k, v in enumerate(pages):
            if v.xpath('./text()').extract()[0] == u'下一页':
                index = str(k)
                break
        max_page = sel.xpath('//div[@id="pagenav"]/a[' + index + ']/text()').extract()[0]

        url = response.url
        print(url, '---max_page---', max_page)
        for page in range(1, int(max_page) + 1):
            request = scrapy.Request(url=url, callback=self.extract_detail_link, dont_filter=True)
            request.meta['page'] = page
            yield request

    def extract_detail_link(self, response):
        sel = scrapy.Selector(response)
        hk_firm = sel.xpath('//table[@id="fixed"]/tbody/tr')
        for k, firm in enumerate(hk_firm):
            if k == 0:
                continue
            detail_link = ''.join(firm.xpath('./td[2]/a/@href').extract())
            request = scrapy.Request(url=detail_link, callback=self.get_item)
            # 详情页面不需要加载JS
            request.meta['NoJS'] = True
            yield request

    def get_item(self, response):
        sel = scrapy.Selector(response)
        item = items.StockCodeItem()
        item['name'] = ''.join(sel.xpath('//span[@class="quote_title_0 wryh"]/text()').extract())
        item['code'] = ''.join(sel.xpath('//span[@class="quote_title_1 wryh"]/text()').extract())
        item['stock_exchange'] = 'US'
        yield item
