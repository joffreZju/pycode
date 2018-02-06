# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy import Request
from scrapy import Selector
from neeuspider.items import BrandItem

class BrandSpider(Spider):
    name = "brandspider"
    start_urls = ['http://www.neeu.com/brand/home.html']

    def parse(self, response):
        bpress_url = 'http://www.neeu.com/brand/press.jsp'
        response.body.decode("gbk")
        sel = Selector(response)
        brands = sel.xpath('//div[@class="brandname"]/ul//li')
        for brand in brands:
            item = BrandItem()
            count = brand.xpath('count(.//a[@href])')[0].extract()
            int_count = int(float(count))
            if int_count == 2:
                item['eng_name'] = brand.xpath('.//a[@href][1]/text()')[0].extract()
                item['chn_name'] = brand.xpath('.//a[@href][2]/text()')[0].extract()
            elif int_count == 1:
                item['eng_name'] = brand.xpath('.//a[@href]/text()')[0].extract()
                item['chn_name'] = ""
            #将提取到的品牌URL替换为该品牌咨询所在的URL:bpress_url
            news_href = brand.xpath('./h4/a[@href]/@href')[0].extract().replace("/brand", bpress_url)
            item['news_href'] = news_href
            yield item