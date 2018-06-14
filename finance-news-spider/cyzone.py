# -*- coding: utf-8 -*-

import time
import datetime
import pymongo
import pandas
import requests
from lxml import etree
from selenium import webdriver, common
import selenium

conn = pymongo.MongoClient('10.214.224.142', 20000)
db = conn['finance_news']


def search(name: str, browser):
    # browser.implicitly_wait(3)
    ele = browser.find_element_by_class_name('search-btn')
    ele.click()
    ele = browser.find_element_by_class_name('search-t')
    ele.clear()
    ele.send_keys(name)
    ele = browser.find_element_by_class_name('search-btn')
    ele.click()

    tab1 = browser.current_window_handle
    for tab in browser.window_handles:
        if tab == tab1:
            continue
        browser.switch_to.window(tab)
        try:
            browser.find_element_by_class_name('no-result')
        except selenium.common.exceptions.NoSuchElementException:
            print(name, ',有搜索结果')
        finally:
            browser.close()

    browser.switch_to.window(tab1)


def get_company_from_excel() -> list:
    df = pandas.read_excel('orgNames.xlsx')
    names = []
    for name in df['公司名']:
        names.append(name)
    return names


def search_companies_in_excel():
    driver = webdriver.Chrome()
    driver.get('http://www.cyzone.cn')

    # search_company('小米', driver)
    # search_company('瀚华金控股份有限公司', driver)
    # search_company('江苏通金所股权投资基金管理有限公司', driver)

    companies = get_company_from_excel()
    for i in range(0, len(companies)):
        try:
            search(companies[i], driver)
        except Exception as e:
            print(e)
            print(i, '当前出错的位置')

        if i % 200 == 0 and i != 0:
            driver.quit()
            time.sleep(3)
            driver = webdriver.Chrome()
            driver.get('http://www.cyzone.cn')


if __name__ == '__main__':
    pass
