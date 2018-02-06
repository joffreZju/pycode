# -*- coding:utf-8 -*-
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor
from scrapy import Selector,Request
from vogue import items
import re

class VogueSpider(CrawlSpider):
    name = "vogue"
    start_urls = [
        "http://brand.vogue.com.cn",
        # "http://brand.vogue.com.cn/Chanel/",
        # "http://brand.vogue.com.cn/Dior/",
        # "http://brand.vogue.com.cn/Hermes/",
        # "http://brand.vogue.com.cn/Coach/",
        # "http://brand.vogue.com.cn/Furla/",
        # "http://brand.vogue.com.cn/Prada/",
        # "http://brand.vogue.com.cn/Fendi/",
        # "http://brand.vogue.com.cn/Clinique/",
        # "http://brand.vogue.com.cn/SK-II/",
        # "http://brand.vogue.com.cn/OLAY/",
        # "http://brand.vogue.com.cn/LANEIGE/",
        # "http://brand.vogue.com.cn/Sulwhasoo/",
        # "http://brand.vogue.com.cn/Mode-Creation-Munich/",
        # "http://brand.vogue.com.cn/Givenchy/",
        # "http://brand.vogue.com.cn/Longchamp/",
    ]
    rules = (
        Rule(LinkExtractor(allow=(), restrict_xpaths=('//ul[@class="ul_brands01 clearfix"]/li/a')),
        follow=True,
        callback='parse_item'), 
    )

    # def parse(self, response):
    def parse_item(self,response):
        sel = Selector(response)
        infos = sel.xpath('//ul[@class="ul02"]/li')
        item = items.VogueItem()
        info_dict = {}
        for info in infos:
            key = ''.join( info.xpath('./text()').extract() ).strip(u' ').strip(u'：')
            value = ''.join( info.xpath('.//span/text()').extract() )
            if key == u'英文名称' and 'brand_name' not in item:
                item['brand_name'] = value
            elif key == u'英文简称':
                item['brand_name'] = value
            elif key == u'中文名称':
                item['cn_brand_name'] = value
            else:
                info_dict[key] = value
        item['about'] = info_dict

        # Hermes 和 MCM 与微博数据不统一
        if 'cn_brand_name' in item and item['cn_brand_name'] == u'爱马仕':
            item['brand_name'] = u'Hermes'

        a = sel.xpath('//div[@class="tabLinks"]//text()').extract()
        b = [ i for i in a if i!=u'\r\n' and i!=u'|' ]
        kinds_dict = {}
        kinds_child = [] 
        for i in b:
            if u'\r\n' in i:
                key = i.strip(u'\r\n')
                if 'cn_brand_name' in item:
                    key = key.strip(item['cn_brand_name'])
                if 'brand_name' in item:
                    key = key.strip(item['brand_name'])

                kinds_child = []
                kinds_dict[key] = kinds_child
            else:
                kinds_dict[key].append(i)
        item['products'] = kinds_dict
        
        story_url = ''.join( sel.xpath('//div[@class="cap"]/h2[@class="smallNav"]/a/@href').re('\S+brandstory.html') )
        r = Request(story_url,callback=self.parse_story)
        r.meta['item'] = item
        yield  r

    def parse_story(self,response):
        item = response.meta['item']
        sel = Selector(response)
        hs_list =[]
        
        hs = sel.xpath('//ul[@class = "brand-history"]/li')
        for h in hs:
            date = ''.join( h.xpath('./span//text()').extract() )
            event = ''.join( h.xpath('./p//text()').extract() )
            hs_list.append( { 'date' : date, 'event':event } )
        if len(hs_list) > 0:
            item['history'] = hs_list
        
        # 品牌故事中可能包含品牌历史
        text = sel.xpath('//div[@class = "para"]/p//text()').extract()

        if 'history' in item or u'品牌历史：' not in text:
            item['story'] = text
        else:
            index = text.index(u'品牌历史：')
            item['story'] = text[0:index]
            for i in range( index+1,len(text) ):
                #针对 SK-II
                if u'年：' in text[i]:
                    j = text[i].find(u'年：')
                    hs_list.append( { 'date' : text[i][0:j+2], 'event' : text[i][j+2:] } )
                elif u'月：' in text[i]:
                    j = text[i].find(u'月：')
                    hs_list.append( { 'date' : text[i][0:j+2], 'event' : text[i][j+2:] } )    
                elif u'日：' in text[i]:
                    j = text[i].find(u'日：')
                    hs_list.append( { 'date' : text[i][0:j+2], 'event' : text[i][j+2:] } )
                # 针对Sulwhasoo 
                else:
                    year = re.search(r'\d{4}',text[i])
                    if year:
                        year = year.group()
                        hs_list.append( { 'date' : year, 'event' : text[i].strip(year).strip(' ') } )
            
            item['history'] = hs_list

        yield item

