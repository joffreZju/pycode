# -*- coding:utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy import Selector, Request
from kaola import items
import re


class KaolaSpider(CrawlSpider):
    name = "kaola"
    start_urls = [
        'http://www.kaola.com/search.html?key=coach&pageNo=1&type=2&pageSize=60&isStock=false&isSelfProduct=false&isDesc=true&brandId=&proIds=&isSearch=0&isPromote=false&backCategory=&country=&lowerPrice=-1&upperPrice=-1&changeContent=type',

        'http://www.kaola.com/search.html?key=chanel&pageNo=1&type=2&pageSize=60&isStock=false&isSelfProduct=false&isDesc=true&brandId=&proIds=&isSearch=0&isPromote=false&backCategory=&country=&lowerPrice=-1&upperPrice=-1&changeContent=type',

        'http://www.kaola.com/search.html?key=dior&pageNo=1&type=2&pageSize=60&isStock=false&isSelfProduct=false&isDesc=true&brandId=&proIds=&isSearch=0&isPromote=false&backCategory=&country=&lowerPrice=-1&upperPrice=-1&changeContent=type',

        'http://www.kaola.com/search.html?key=%25E7%2588%25B1%25E9%25A9%25AC%25E4%25BB%2595%25E5%25A5%25B3%25E5%25A3%25AB&pageNo=1&type=2&pageSize=60&isStock=false&isSelfProduct=false&isDesc=true&brandId=&proIds=&isSearch=0&isPromote=false&backCategory=&country=&lowerPrice=-1&upperPrice=-1&changeContent=type',

        'http://www.kaola.com/search.html?key=%25E8%258A%2599%25E6%258B%2589%25E6%2596%259C%25E6%258C%258E%25E5%258C%2585&pageNo=1&type=2&pageSize=60&isStock=false&isSelfProduct=false&isDesc=true&brandId=&proIds=&isSearch=0&isPromote=false&backCategory=&country=&lowerPrice=-1&upperPrice=-1&changeContent=type',

        'http://www.kaola.com/search.html?key=prada&pageNo=1&type=2&pageSize=60&isStock=false&isSelfProduct=false&isDesc=true&brandId=&proIds=&isSearch=0&isPromote=false&backCategory=&country=&lowerPrice=-1&upperPrice=-1&changeContent=type',

        'http://www.kaola.com/search.html?key=fendi&pageNo=1&type=2&pageSize=60&isStock=false&isSelfProduct=false&isDesc=true&brandId=&proIds=&isSearch=0&isPromote=false&backCategory=&country=&lowerPrice=-1&upperPrice=-1&changeContent=type',

        'http://www.kaola.com/search.html?key=%25E5%2580%25A9%25E7%25A2%25A7%25E6%25B0%25B4&pageNo=1&type=2&pageSize=60&isStock=false&isSelfProduct=false&isDesc=true&brandId=&proIds=&isSearch=0&isPromote=false&backCategory=&country=&lowerPrice=-1&upperPrice=-1&changeContent=type',

        'http://www.kaola.com/search.html?key=SK-II&pageNo=1&type=2&pageSize=60&isStock=false&isSelfProduct=false&isDesc=true&brandId=&proIds=&isSearch=0&isPromote=false&backCategory=&country=&lowerPrice=-1&upperPrice=-1&changeContent=type',

        'http://www.kaola.com/search.html?key=OLAY&pageNo=1&type=2&pageSize=60&isStock=false&isSelfProduct=false&isDesc=true&brandId=&proIds=&isSearch=0&isPromote=false&backCategory=&country=&lowerPrice=-1&upperPrice=-1&changeContent=type',

        'http://www.kaola.com/search.html?key=laneige%25E5%2585%25B0%25E8%258A%259D&pageNo=1&type=2&pageSize=60&isStock=false&isSelfProduct=false&isDesc=true&brandId=&proIds=&isSearch=0&isPromote=false&backCategory=&country=&lowerPrice=-1&upperPrice=-1&changeContent=type',

        'http://www.kaola.com/search.html?key=%25E9%259B%25AA%25E8%258A%25B1%25E7%25A7%2580&pageNo=1&type=2&pageSize=60&isStock=false&isSelfProduct=false&isDesc=true&brandId=&proIds=&isSearch=0&isPromote=false&backCategory=&country=&lowerPrice=-1&upperPrice=-1&changeContent=type',

        'http://www.kaola.com/search.html?key=MCM&pageNo=1&type=2&pageSize=60&isStock=false&isSelfProduct=false&isDesc=true&brandId=&proIds=&isSearch=0&isPromote=false&backCategory=&country=&lowerPrice=-1&upperPrice=-1&changeContent=type',

        'http://www.kaola.com/search.html?key=%25E7%25BA%25AA%25E6%25A2%25B5%25E5%25B8%258C%25E5%25AE%259A%25E5%25A6%2586&pageNo=1&type=2&pageSize=60&isStock=false&isSelfProduct=false&isDesc=true&brandId=&proIds=&isSearch=0&isPromote=false&backCategory=&country=&lowerPrice=-1&upperPrice=-1&changeContent=type',

        'http://www.kaola.com/search.html?key=longchamp%25E5%258D%2595%25E8%2582%25A9&pageNo=1&type=2&pageSize=60&isStock=false&isSelfProduct=false&isDesc=true&brandId=&proIds=&isSearch=0&isPromote=false&backCategory=&country=&lowerPrice=-1&upperPrice=-1&changeContent=type',

    ]

    rules = (
        # Rule(LinkExtractor(allow=('/product/'), restrict_xpaths=('//li[@class="goods"]/div/div[1]')),
        #     follow=True,
        #     callback='parse_item'),
        Rule(LinkExtractor(allow=(), restrict_xpaths=('//a[@class="nextPage"]')),
             follow=True,
             callback='parse'),
    )

    def parse_start_url(self, response):
        sel = Selector(response)
        goods = sel.xpath('//ul[@id="result"]/li')
        currPage = ''.join(sel.xpath('//span[@class="num"]/i/text()').extract()).strip()
        i = 1
        for good in goods:
            item = items.KaolaItem()
            item['rank'] = i + (int(currPage) - 1) * 60
            i += 1
            item['price'] = ''.join(good.xpath('.//*/*/p[@class="price"]/span[1]/text()').extract()).strip()
            item['market_price'] = ''.join(good.xpath('.//*/*/p[@class="price"]/span[2]/del/text()').extract()).strip()
            tmp = good.xpath('.//div/div[@class="img"]/a/@href').extract()[0]
            detailUrl = "http://www.kaola.com"
            if "http://" not in tmp:
                detailUrl = detailUrl + tmp
            else:
                detailUrl = tmp

            # item['proUrl'] = tmp            
            item['product_id'] = re.search('\d+', tmp).group()
            r = Request(detailUrl, callback=self.parse_item)
            r.meta['item'] = item
            yield r

    def parse_item(self, response):
        item = response.meta['item']
        sel = Selector(response)
        tmp = ''.join(sel.xpath('//dt[@class="product-title"]/text()').extract()).strip()
        if tmp.find(u"】") != -1:
            item['product_name'] = tmp[tmp.index(u"】") + 1:]
        else:
            item['product_name'] = tmp
        item['comment_num'] = ''.join(sel.xpath('//b[@id="commentCounts"]/text()').extract()).strip()
        params = sel.xpath('//ul[@class="goods_parameter"]/li')

        for param in params:
            text = ''.join(param.xpath('.//text()').extract()).strip()
            if u"商品品牌" in text:
                item['brand_name'] = text[text.index(u"：") + 1:]
                if u'爱马仕' in item['brand_name']:
                    item['brand_name'] = "HERMES"
                elif u'兰芝' in item['brand_name']:
                    item['brand_name'] = "LANEIGE"
            elif u"产品类型" in text:
                item['product_type'] = text[text.index(u"：") + 1:]
            elif u"人群" in text:
                item['people_aimed'] = text[text.index(u"：") + 1:]

        yield item
