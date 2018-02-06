# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy import Selector
from scrapy import Request
from yokaspider.items import BrandItem, NewsItem
from yokaspider import tools
from yokaspider.pagetype import newspage_type
from yokaspider.tools import URL_NO_FILTER
import logging
import re

class YokaNewsSpider(Spider):
    name = 'yoka_news_spider'
    start_urls = ['http://brand.yoka.com/brandlist.htm']

    def __init__(self):
        super(YokaNewsSpider, self).__init__()
        self.backupCharset = 'gb18030'
        self.count = 0
        URL_NO_FILTER.union(set(YokaNewsSpider.start_urls))

    # 抓取品牌列表页面上的品牌链接
    def parse(self, response):
        self.response_body_decode(response)
        sel = Selector(response)
        # 获取所有的品牌链接
        homeurl = tools.getHomeUrl(response.url)
        brandlist = sel.xpath('//div[@class="mask"]//ul//li//a//@href').extract()
        brandlist.extend(sel.xpath('//div[@class="imgShow"]/dl/dt/a/@href').extract())
        for brand in brandlist:
            url = homeurl + brand
            URL_NO_FILTER.add(url)
            URL_NO_FILTER.add(url + '/')
            yield Request(url, callback=self.parseMainPage)

    # 解析品牌主页面上的品牌信息、商品和新闻链接等
    def parseMainPage(self, response):
        self.response_body_decode(response)
        sel = Selector(response)
        homeurl = tools.getHomeUrl(response.url)
        # 提取品牌英文名和中文名
        names = sel.xpath('//div[@class="brandProfile"]/dl[@class="profile clearfix"]\
        /dd[@class="detail"]//a//text()').extract()
        # 上部所有链接
        all_links = sel.xpath('//div[@class="m-nav mb0"]//a//@href').extract()
        # 提取到新闻链接 /coach/news/
        newsMore = all_links[5]
        if len(names) == 2:
            chn_name = names[0]
            eng_name = names[1]
        elif len(names) == 1:
            chn_name = eng_name = names[0]
        else:
            raise Exception('can not extract names from this brand' + response.url)
        branditem = BrandItem()
        branditem['chn_name'] = chn_name
        branditem['eng_name'] = eng_name
        branditem['url'] = response.url
        yield branditem
        # 生成新闻链接请求
        url = homeurl + newsMore
        URL_NO_FILTER.add(url)
        r = Request(url, callback=self.parseNewsList)
        r.meta['brandname'] = eng_name
        yield r

    # 解析新闻列表页面
    def parseNewsList(self, response):
        self.response_body_decode(response)
        sel = Selector(response)
        brandname = response.meta['brandname']
        # 获取当前新闻列表页面上的所有新闻链接
        allnews = sel.xpath('//div[@class="contents"]//div[@class="m-pictrues"]//dl//dt//a//@href').extract()
        # 获取当前页面的根网址
        homeurl = tools.getHomeUrl(response.url)
        for news in allnews:
            # http://www.yoka.com/fashion/model/2016/0914/pic48925501135097.shtml?source=brand
            self.count = self.count + 1
            print "News crawled" + str(self.count)
            if news.count("http:") == 0:
                news = homeurl + news
            r = Request(news, callback=self.parseNews)
            r.meta['brandname'] = brandname
            yield r
        # 解析是否有下一页
        nextpage = sel.xpath('//div[@class="contents"]//div[@class="m-page"]//a[@class="pg_next"]//@href').extract()
        if len(nextpage) > 0:
            url = homeurl + nextpage[0]
            URL_NO_FILTER.add(url)
            r = Request(url, callback=self.parseNewsList)
            r.meta['brandname'] = brandname
            yield r

    def parseNews(self, response):
        self.response_body_decode(response)
        sel = Selector(response)
        homeurl = tools.getHomeUrl(response.url)
        brandname = response.meta['brandname']
        news = None    # news保存新闻主体部分的SelectorList
        pagerule = None
        # 判断是否已经可以确定页面规则
        if response.meta.has_key('pagerule'):
            pagerule = response.meta['pagerule']
            news = sel.xpath(pagerule['pageform'])
        else:
            # 对于新闻页面规则库的每条规则进行匹配，然后对该类型的新闻页面进行爬取
            for each_rule in newspage_type.page_rules:
                news = sel.xpath(each_rule['pageform'])
                if len(news) > 0:
                    pagerule = each_rule
                    break
        if pagerule is None:
            raise ValueError('Error processing (' + response.url + ') This page do not have corresponding rules')
        # 获得allpage 和 nextpage url
        if pagerule['allpage'] is None:
            allpage = []
        else:
            allpage = news.xpath(pagerule['allpage']).extract()
        if pagerule['nextpage'] is None:
            nextpage = []
        else:
            nextpage = news.xpath(pagerule['nextpage']).extract()
        # 如果包含全页阅读的url，则进行该处理
        if len(allpage) > 0:
            if tools.isCompleteUrl(allpage[0]):
                url = allpage[0]
            else:
                url = homeurl + allpage[0]
            r = Request(url, callback=self.parseNews)
            r.meta['brandname'] = brandname
            r.meta['pagerule'] = pagerule
            yield r
        elif len(nextpage) > 0:
            # 如果包含下一页，则进行该处理
            if tools.isCompleteUrl(nextpage[0]):
                url = nextpage[0]
            else:
                url = homeurl + nextpage[0]
            # 提取当前页面的title, date, content，保存到article中，传递至下一请求
            title = news.xpath(pagerule['title']).extract()
            date = self.getDate(news, response.url, pagerule['date'])
            content = self.getContent(news, pagerule['content'])
            article = {'brandname': brandname,
                       'title': title,
                       'date': date,
                       'content': content}
            r = Request(url, callback=self.parseNextPage)
            r.meta['article'] = article
            r.meta['pagerule'] = pagerule
            yield r
        else:
            # 如果新闻只有一页，则直接提取新闻内容
            title = news.xpath(pagerule['title']).extract()
            date = self.getDate(news, response.url, pagerule['date'])
            content = self.getContent(news, pagerule['content'])
            item = NewsItem()
            item['brandname'] = brandname
            item['date'] = date
            item['title'] = "".join(title)
            item['content'] = "".join(content)
            yield item

    # 解析每条新闻的下一页
    def parseNextPage(self, response):
        self.response_body_decode(response)
        sel = Selector(response)
        homeurl = tools.getHomeUrl(response.url)
        article = response.meta['article']
        pagerule = response.meta['pagerule']
        new_title = "".join(sel.xpath(pagerule['title']).extract())
        old_title = "".join(article['title'])
        if len(old_title) > 5:
            isequal = cmp(new_title[0:5], old_title[0:5])
        else:
            isequal = cmp(new_title, old_title)

        # 判断新的正文是否出现过，this may not have any uses
        if isequal == 0:
            next_page = []
        else:
            new_content = self.getContent(sel, pagerule['content'])
            if set(new_content).issubset(set(article['content'])) is False:
                article['content'].extend(new_content)
            next_page = sel.xpath(pagerule['nextpage']).extract()
        if len(next_page) > 0:
            # 判断是否有下一页, 如果有则继续发起请求
            if tools.isCompleteUrl(next_page[0]):
                url = next_page[0]
            else:
                url = homeurl + next_page[0]
                # 提取当前页面的title, date, content，保存到article中，传递至下一请求
            r = Request(url, callback=self.parseNextPage)
            r.meta['article'] = article
            r.meta['pagerule'] = pagerule
            yield r
        else:
            # 如果没有下一页，则yield item
            item = NewsItem()
            item['brandname'] = article['brandname']
            item['date'] = article['date']
            item['title'] = "".join(article['title'])
            item['content'] = "".join(article['content'])
            yield item


    # 从页面获取新闻正文
    # 返回Unicode string list
    def getContent(self, newspage, content_rule_list):
        content = []
        for content_rule in content_rule_list:
            content.extend(newspage.xpath(content_rule).extract())
        return content


    # 从页面和url中获取Date
    # 返回string
    def getDate(self, newspage, url, daterule):
        if daterule is not None:
            date_str = newspage.xpath(daterule).extract()
            # 2012-02-23  or 2012-02-03
            pattern = re.compile(r'(\d{4}-\d{2}-\d{2})')
            date = re.search(pattern, date_str[0]).group()
            return date
        #若datarule 为None, 则尝试从url中截取date
        date_pattern = re.compile(r'(\d{4})/(\d{4})')
        sresult = re.search(date_pattern, url)
        if sresult is None:
            date_str = ""
        else:
            date_str = sresult.group()
        try:
            index = date_str.index('/')
            sub = date_str[index:index + 3]
            date = date_str.replace(sub, sub + '-').replace('/', '-')
        except ValueError:
            date = ""
        return date


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

