# -*- coding: utf-8 -*-

import time
import datetime
import random
import pymongo
import pandas as pd
import requests
from lxml import etree, html
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
    df = pd.read_excel('orgNames.xlsx')
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


def get_basic_info_of_one_company(page_url: str):
    col = db['cyzone_companies']
    resp = requests.get(page_url)
    if resp.status_code != 200:
        print(page_url, 'status code = ', resp.status_code)
        time.sleep(5)

    trs = etree.HTML(resp.text).xpath("//tr[@class='table-plate2']")
    for tr in trs:
        company_url = tr.xpath("./td[2]/a/@href")[0]
        c = {
            'name': tr.xpath("./td[2]/a/span/text()")[0],
            'founding_time': tr.xpath("./td[3]/text()")[0],
            'cases_count': tr.xpath("./td[4]/text()")[0],
            'img': tr.xpath("./td[1]/a/img/@src")[0],
            'cyzone_url': company_url,
        }
        preferences = []
        for i in tr.xpath("./td[5]/text()"):
            if len(i.strip()) != 0:
                preferences.append(i.strip())
        fields = []
        for i in tr.xpath("./td[6]/text()"):
            if len(i.strip()) != 0:
                fields.append(i.strip())
        c['preferences'] = preferences
        c['fields'] = fields
        col.replace_one(
            {
                'company_url': company_url
            },
            c, upsert=True
        )


def get_basic_info_of_all_companies():
    for page in range(1, 123):
        url = 'http://www.cyzone.cn/company/list-0-' + str(page) + '-4/'
        # print(url)
        try:
            get_basic_info_of_one_company(url)
            print('complete page number:', page)
            time.sleep(3)
        except Exception as e:
            print(url, e)


def get_detail_info_of_one_company(url: str, col):
    if len(url) <= len('http://www.cyzone.cn/d/'):
        return

    resp = requests.get(url)
    if resp.status_code != 200:
        print(url, 'status code = ', resp.status_code)
        return

        # sel = etree.HTML(resp.text)
    sel = html.fromstring(resp.text)
    name = sel.xpath("//li[@class='organize']//text()")[0]

    official_site = sel.xpath("//div[@class='ti-left pull-left']//li/a/@href")
    official_site = official_site[0] if official_site is not None and len(official_site) > 0 else None

    description = sel.find_class(class_name='people-info-box')
    description = description[0].text_content().strip() if description is not None and len(description) > 0 else None

    # tmp = sel.xpath("//div[@class='people-info-box']/p/a/text()")
    # tmp = tmp[0] if tmp is not None and len(tmp) > 0 else None
    # description = sel.xpath("//div[@class='people-info-box']/p//text()")
    # description = description[0] if description is not None else None
    # description = tmp + description if tmp is not None else description

    team = []
    for p in sel.xpath("//div[@class='team clearfix look']//li/div[@class='team-info']"):
        job = p.xpath("./p[@class='job']/text()")
        job = job[0] if job is not None and len(job) > 0 else None
        p_name = p.xpath("./p[@class='name']//text()")
        p_name = p_name[0] if p_name is not None and len(p_name) > 0 else None
        p_url = p.xpath("./p[@class='name']/a/@href")
        p_url = p_url[0] if p_url is not None and len(p_url) > 0 else None
        team.append({
            'people_name': p_name,
            'job': job,
            'people_url': p_url,
        })
        # print(p_name, job, p_url)

    print(name, official_site, 'team-member-count:', len(team))

    col.find_one_and_update(
        {
            'cyzone_url': url
        },
        {
            '$set': {
                'name': name,
                'official_site': official_site,
                'description': description,
                'team': team,
            }
        }
    )


def get_detail_info_of_all_companies():
    col = db['cyzone_companies']
    urls = col.find({'team': {'$exists': False}}, {'_id': 0, 'cyzone_url': 1})
    for u in urls:
        try:
            get_detail_info_of_one_company(u['cyzone_url'], col)
            time.sleep(3)
        except Exception as e:
            print(e)
            time.sleep(10)


def get_invested_cases_of_all_companies():
    options = webdriver.ChromeOptions()
    options.add_argument(
        "--user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'")

    driver = webdriver.Chrome(options=options)
    col = db['cyzone_companies']
    urls = col.find(
        {
            'cases_count': {'$ne': '0'},
            'invested_companies': {'$exists': False},
        },
        {'_id': 0, 'cyzone_url': 1}
    )
    for u in urls:
        try:
            get_invested_cases_of_one_company(u['cyzone_url'], driver, col)
            time.sleep(random.randint(6, 10))
        except Exception as e:
            print(e)
            time.sleep(random.randint(5, 10))


def get_invested_cases_of_one_company(url: str, driver=None, col=None):
    driver.get(url)
    driver.execute_script("scroll(0,document.body.scrollHeight)")
    ele = driver.find_element_by_xpath("//div[@class='check-more2']/a")
    ele.click()

    invested_companies = []
    while True:
        invested_companies += get_invest_cases_of_one_company_in_one_page(driver)
        driver.execute_script("scroll(0,document.body.scrollHeight)")
        time.sleep(random.randint(6, 13))

        try:
            page = driver.find_element_by_xpath("//div[@id='pages']/span[@class='current']")
        except Exception as e:
            print(e)
            break

        if page is None:
            print('current page is None')
            break

        completed = True
        next_page = int(page.text) + 1
        for a in driver.find_elements_by_xpath("//div[@id='pages']/a"):
            if a.text.strip() == str(next_page):
                completed = False
                a.click()
                # print('click next page', next_page)
                break

        if completed:
            print('completed one company: ', url)
            break

    if len(invested_companies) > 0:
        col.find_one_and_update(
            {
                'cyzone_url': url
            },
            {
                '$set': {'invested_companies': invested_companies, }
            }
        )


def get_invest_cases_of_one_company_in_one_page(driver=None) -> list:
    res = []
    print('current page url:', driver.current_url)
    for tr in driver.find_elements_by_xpath("//tr[@class='table-plate3']"):
        names = tr.find_element_by_xpath("./td[@class='tp2']").text
        names = ','.join(names.split('\n'))
        money = tr.find_element_by_xpath("./td[@class='tp-mean']/div[@class='money']").text
        rounds = tr.find_element_by_xpath("./td[4]").text
        investors = tr.find_element_by_xpath("./td[@class='tp3']").get_attribute('title')
        fields = tr.find_element_by_xpath("./td[6]").text
        invest_time = tr.find_element_by_xpath("./td[7]").text
        tmp = {
            'names': names,
            'money': money,
            'rounds': rounds,
            'investors': investors,
            'field': fields,
            'invest_time': invest_time,
        }
        print(tmp)
        res.append(tmp)
    return res


if __name__ == '__main__':
    # search_companies_in_excel()
    # get_basic_info_of_all_companies()

    # get_detail_info_of_one_company('http://www.cyzone.cn/d/20150710/2025.html', col=db['cyzone_companies'])
    # get_detail_info_of_all_companies()

    # chrome = webdriver.Chrome()
    # collection = db['cyzone_companies']
    # get_invested_cases_of_one_company('http://www.cyzone.cn/d/20160505/2283.html', chrome, collection)
    # get_invested_cases_of_one_company('http://www.cyzone.cn/d/20160315/2203.html', chrome, collection)
    # get_invested_cases_of_one_company('http://www.cyzone.cn/d/20160926/2850.html', chrome, collection)

    # get_invested_cases_of_all_companies()

    pass
