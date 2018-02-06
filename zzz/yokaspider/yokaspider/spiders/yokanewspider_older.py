# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy import Selector
from scrapy import Request
from yokaspider.items import BrandItem, NewsItem
from yokaspider import tools
import re
import logging

class YokaSpider(Spider):
    name = 'yoka_news_spider_old'
    start_urls = ['http://brand.yoka.com/brandlist.htm']

    def __init__(self):
        super(YokaSpider, self).__init__()
        self.homeurl = 'http://brand.yoka.com'
        self.backupCharset = 'gb18030'

    # 抓取品牌列表页面上的品牌链接
    def parse(self, response):
        charset = tools.detectPageCharset(response.body)
        if charset is not None:
            try:
                response.body.decode(charset)
            except UnicodeDecodeError:
                response.body.decode(self.backupCharset)
        else:
            logging.log(logging.WARNING, "Can not detect the charset encoding of " + response.url)
        sel = Selector(response)
        # 获取所有的品牌链接
        brandlist = sel.xpath('//div[@class="mask"]//ul//li//a//@href').extract()
        brandlist.extend(sel.xpath('//div[@class="imgShow"]/dl/dt/a/@href').extract())
        for brand in brandlist:
            url = self.homeurl + brand
            yield Request(url, callback=self.parseMainPage)

    # 解析品牌主页面上的品牌信息、商品和新闻链接等
    def parseMainPage(self, response):
        charset = tools.detectPageCharset(response.body)
        if charset is not None:
            try:
                response.body.decode(charset)
            except UnicodeDecodeError:
                response.body.decode(self.backupCharset)
        else:
            logging.log(logging.WARNING, "Can not detect the charset encoding of " + response.url)
        sel = Selector(response)
        # 提取品牌英文名和中文名
        names = sel.xpath('//div[@class="brandProfile"]/dl[@class="profile clearfix"]'\
                          '/dd[@class="detail"]//a//text()').extract()
        # 上部所有链接
        all_links = sel.xpath('//div[@class="m-nav mb0"]//a//@href').extract()
        # 提取到新闻链接 /coach/news/
        newsMore = all_links[5]
        # 品牌论坛链接 http://bbs.yoka.com/forumdisplay_pic.php?fid=235&brand_view=1
        # forum = all_links[4]
        # 商品列表的链接 /coach/productlist.htm
        # productlist = all_links[2]
        # not used products = sel.xpath('//div[@class="sub-nav sub-nav-ds"]//a//@href').extract()
        if len(names) == 2:
            chn_name = names[0]
            eng_name = names[1]
        elif len(names) == 1:
            eng_name = names[0]
            chn_name = ""
        else:
            raise Exception('can not extract names from this brand' + response.url)
        branditem = BrandItem()
        branditem['chn_name'] = chn_name
        branditem['eng_name'] = eng_name
        yield branditem
        # 生成新闻链接请求
        url = self.homeurl + newsMore
        r = Request(url, callback=self.parseNewsList)
        r.meta['brandname'] = eng_name
        yield r
        # 生成品牌论坛链接请求
        # http://bbs.yoka.com/forumdisplay_pic.php?fid=235&brand_view=1
        # url = forum.replace('forumdisplay_pic', 'forumdisplay')
        # r = Request(url, callback=self.parseForumList)
        # r.meta['brandname'] = eng_name
        # yield r
        # # 生成商品列表请求
        # url = self.homeurl + productlist
        # r = Request(url, callback=self.parseProductList)
        # r.meta['brandname'] = eng_name
        # yield r

    # 解析新闻列表页面
    def parseNewsList(self, response):
        charset = tools.detectPageCharset(response.body)
        if charset is not None:
            try:
                response.body.decode(charset)
            except UnicodeDecodeError:
                response.body.decode(self.backupCharset)
        else:
            logging.log(logging.WARNING, "Can not detect the charset encoding of " + response.url)
        sel = Selector(response)
        brandname = response.meta['brandname']
        # 获取当前新闻列表页面上的所有新闻链接
        allnews = sel.xpath('//div[@class="contents"]//div[@class="m-pictrues"]//dl//dt//a//@href').extract()
        for news in allnews:
            # http://www.yoka.com/fashion/model/2016/0914/pic48925501135097.shtml?source=brand
            if news.count("http:") == 0:
                news = self.homeurl + news
            r = Request(news, callback=self.parseNews)
            r.meta['brandname'] = brandname
            yield r
        # 解析是否有下一页
        nextpage = sel.xpath('//div[@class="contents"]//div[@class="m-page"]//a[@class="pg_next"]//@href').extract()
        if len(nextpage) > 0:
            url = self.homeurl + nextpage[0]
            r = Request(url, callback=self.parseNewsList)
            r.meta['brandname'] = brandname
            yield r

    # 解析每条新闻页面的内容
    def parseNews(self, response):
        charset = tools.detectPageCharset(response.body)
        if charset is not None:
            try:
                response.body.decode(charset)
            except UnicodeDecodeError:
                response.body.decode(self.backupCharset)
        else:
            logging.log(logging.WARNING, "Can not detect the charset encoding of " + response.url)
        sel = Selector(response)
        brandname = response.meta['brandname']
        page_type = sel.xpath('//div[@class="contents"]/div[@id="brand-right"]/div[@class="m-zx-lbox"]')
        page_type2 = sel.xpath('//div[@class="g-content clearfix m-first"]/div[@class="first clearfix"]/div[@class="g-main fleft"]')
        page_type3 = sel.xpath('//div[@class="g-content clearfix articlePic"]')
        page_type4 = sel.xpath('//div[@class="centess"]//div[@id="pardynr"]')
        page_type5 = sel.xpath('//div[@id="content94"]//div[@class="con2_left_row1"]')
        if len(page_type) > 0:
            # page_type 官方发布的新闻页面
            title = page_type.xpath('./h1/text()').extract()
            date = page_type.xpath('./dl[@class="date"]/dt/span[1]/text()').extract()
            content = page_type.xpath('./div[@class="main"]//p//text()').extract()
        elif len(page_type2) > 0:
            # page_type2 编辑写的页面
            all_pages = page_type2.xpath('./dl[@class="pages_fullRead"]/dd/a/@href').extract()
            if len(all_pages) > 0:
                # 如果包含全页阅读 需重新生成请求
                url = "http://www.yoka.com" + all_pages[0]
                r = Request(url, callback=self.parseNews)
                r.meta['brandname'] = brandname
                yield r
                return
            else:
                print 'page type 2 llllllllllllllllllllllll'
                title = page_type2.xpath('./h1[@class="infoTitle"]/text()').extract()
                date = page_type2.xpath('./div[@class="infoTime"]/div[@class="time"]/i/text()').extract()
                content = page_type2.xpath('./div[@class="double_quotes"]/div/text()').extract()
                content.extend(page_type2.xpath('./div[@class="textCon"]//p//text()').extract())
        elif len(page_type3) > 0:
            # page_type3 图片幻灯片的新闻页面
            title = page_type3.xpath('./h1[@id="picTitle"]/text()').extract()
            content = page_type3.xpath('./dl[@class="text"]//dd/text()').extract()
            # 从URL中提取日期 http://www.yoka.com/fashion/popinfo/2016/0725/pic48495001119565.shtml?source=brand
            date_pattern = re.compile('(\d{4})/(\d{4})')
            sresult = re.search(date_pattern, response.url)
            if sresult is None:
                date_str = ""
            else:
                date_str = sresult.group()
            index = date_str.index('/')
            sub = date_str[index:index+3]
            date = date_str.replace(sub, sub + '-').replace('/', '-')
        elif len(page_type4) > 0:
            # page_type4 老版网站的页面 http://www.yoka.com/fashion/roadshow/2008/082290701.shtml
            title = page_type4.xpath('./dl[@class="viewtis"]/dt/h1/text()').extract()
            # 提取日期字符串 如 2008-08-22 11:14 来源：
            date_str = page_type4.xpath('./dl[@class="viewtis"]/dd/text()').extract()
            pattern = re.compile('(\d{4}-\d{2}-\d{2})')
            date = re.search(pattern, date_str[0]).group()
            content = page_type4.xpath('./div[@id="viewbody"]//p//text()').extract()
            # 寻找是否有下一页链接 http://www.yoka.com/fashion/popinfo/2009/0922253399.shtml
            next_page = page_type4.xpath('./div[@id="viewbody"]//span[@class="pagebox_next"]/a/@href').extract()
            if len(next_page) > 0:
                # 如果有下一页链接, 则需要生成新的请求，交给parseNewsNextPage处理
                url = "http://www.yoka.com" + next_page[0]
                r = Request(url, callback=self.parseNewsNextPage)
                article = {'brandname': brandname,
                           'title': title,
                           'date': date,
                           'content': content}
                r.meta['article'] = article
                yield r
                return
        elif len(page_type5) > 0:
            # page_type5 老版网页页面: http://www.yoka.com/luxury/watch/2008/060268802.shtml
            title = page_type5.xpath('./h2/text()').extract()
            # 提取日期字符串 如：2008-06-02 17:12　来源：
            date_str = page_type5.xpath('./div[@class="src"]/text()').extract()
            pattern = re.compile('(\d{4}-\d{2}-\d{2})')
            date = re.search(pattern, date_str[0]).group()
            content = page_type5.xpath('./div[@class="con"]//p//text()').extract()
            # 寻找是否有下一页链接 http://www.yoka.com/luxury/watch/2008/060268802.shtml
            next_page = page_type5.xpath('./div[@class="con"]/p[@align="right"]/a[position()>1 and @style]').extract()
            if len(next_page):
                url = "http://www.yoka.com" + next_page[0]
                r = Request(url, callback=self.parseNewsNextPage)
                article = {'brandname': brandname,
                           'title': title,
                           'date': date,
                           'content': content}
                r.meta['article'] = article
                yield r
                return
        else:
            return
        item = NewsItem()
        item['title'] = "".join(title)
        item['date'] = "".join(date)
        item['brandname'] = brandname
        item['content'] = "".join(content)
        yield item

    # 对于page_type4 和 page_type5，新闻内容会有多页
    # 该方法用来获取所有页面的内容
    def parseNewsNextPage(self, response):
        charset = tools.detectPageCharset(response.body)
        if charset is not None:
            try:
                response.body.decode(charset)
            except UnicodeDecodeError:
                response.body.decode(self.backupCharset)
        else:
            logging.log(logging.WARNING, "Can not detect the charset encoding of " + response.url)
        sel = Selector(response)
        article = response.meta['article']
        page_type4 = sel.xpath('//div[@class="centess"]//div[@id="pardynr"]')
        page_type5 = sel.xpath('//div[@id="content94"]//div[@class="con2_left_row1"]')
        if len(page_type4) > 0:
            # 对 page_type4进行处理
            content = page_type4.xpath('./div[@id="viewbody"]//p//text()').extract()
            # 如果内容重复则不添加
            if set(content).issubset(set(article['content'])):
                article['content'].extend(content)
            next_page = page_type4.xpath('./div[@id="viewbody"]//span[@class="pagebox_next"]/a/@href').extract()
        elif len(page_type5) > 0:
            # 对page_type5 进行处理
            content = page_type5.xpath('./div[@class="con"]//p//text()').extract()
            # 如果内容重复则不添加
            if set(content).issubset(set(article['content'])):
                article['content'].extend(content)
            next_page = page_type5.xpath('./div[@class="con"]/p[@align="right"]/a[position()>1 and @style]').extract()
        else:
            return
        if len(next_page):
            # 如果有下一页链接, 则需要生成新的请求，交给parseNewsNextPage处理
            url = "http://www.yoka.com" + next_page[0]
            r = Request(url, callback=self.parseNewsNextPage)
            r.meta['article'] = article
            yield r
            return
        item = NewsItem()
        item['title'] = "".join(article['title'])
        item['date'] = "".join(article['date'])
        item['brandname'] = article['brandname']
        item['content'] = "".join(article['content'])
        yield item


