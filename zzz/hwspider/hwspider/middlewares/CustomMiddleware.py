# -*- coding: utf-8 -*-
import time
from selenium import webdriver
from scrapy.http import Response
from scrapy.http import HtmlResponse
from scrapy import Request

class CustomMiddleWare(object):
    def __init__(self):
        cap = webdriver.DesiredCapabilities.PHANTOMJS
        cap["phantomjs.page.settings.loadImages"] = False
        self.browser = webdriver.PhantomJS(desired_capabilities=cap)


    def process_request(self, request, spider):
        url = str(request.url)
        if (url.find("Search") == -1):
            return None

        self.browser.get(url)
        time.sleep(1)
        js = "scroll(0,document.body.scrollHeight)"
        self.browser.execute_script(js)
        time.sleep(1)
        content = self.browser.page_source.encode('utf-8')
        return HtmlResponse(url, body=content, status=200)


    def process_response(self, request, response, spider):
        return response

    def __del__(self):
        self.browser.exit()

