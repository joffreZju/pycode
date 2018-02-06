# -*- coding:utf-8 -*-
from scrapy.http import Response, HtmlResponse
from scrapy import Request, signals
import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class JSMiddleware(object):
    def __init__(self):
        cap = webdriver.DesiredCapabilities.PHANTOMJS
        cap['phantomjs.page.settings.loadImages'] = False
        self.browser = webdriver.PhantomJS(desired_capabilities=cap)

    def __del__(self):
        self.browser.close()

    def process_request(self, request, spider):
        if spider.JS and 'NoJS' not in request.meta:
            url = str(request.url)
            self.browser.get(url)
            self.browser.execute_script("location.reload();")
            time.sleep(1)
            wait = WebDriverWait(self.browser, 10)
            input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#pagenum"))
            )
            submit = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#page-go"))
            )
            if 'page' in request.meta:
                page = request.meta['page']
                input.clear()
                input.send_keys(str(page))
                print url, '---current_page---', page

            submit.click()
            time.sleep(1)

            content = self.browser.page_source.encode('gbk')
            return HtmlResponse(url, body=content, request=request, status=200)

    def process_response(self, request, response, spider):
        return response
