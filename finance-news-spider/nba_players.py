# -*- coding: utf-8 -*-

import time
import datetime
import pymongo
import pandas as pd
import requests
from lxml import etree, html
from selenium import webdriver, common
import selenium

conn = pymongo.MongoClient('10.214.224.142', 20000)
db = conn['nba_players']


def get_salaries():
    col = db['salary']
    url = 'https://hoopshype.com/salaries/players/'
    resp = requests.get(url)
    if resp.status_code != 200:
        print('http status code:', resp.status_code)
        return

    sel = html.fromstring(resp.text)
    for tr in sel.xpath("//table[@class='hh-salaries-ranking-table hh-salaries-table-sortable responsive']/tbody/tr"):
        name = tr.xpath("./td[@class='name']/a/text()")[0].strip()
        salary_1718 = tr.xpath("./td[@class='hh-salaries-sorted']/@data-value")[0]
        salary_1819 = tr.xpath("./td[4]/@data-value")[0]
        salary = {
            'name': name,
            'salary_1718': salary_1718,
            'salary_1819': salary_1819,
        }
        col.replace_one(
            {'name': name},
            salary,
            upsert=True,
        )
        print('complete one player: ', name, salary_1718, salary_1819)


def get_stats_of_all_players():
    col = db['stats']
    url = 'http://stats.nba.com/players/list/'
    driver = webdriver.Chrome()
    driver.get(url)

    player_url = []
    for a in driver.find_elements_by_xpath("//li[@class='players-list__name']/a"):
        player_url.append(a.get_attribute('href'))

    for i in range(0, len(player_url)):
        get_stats_of_one_player(player_url[i], driver, col)


def get_stats_of_one_player(url: str, driver=None, collection=None):
    if collection.count({'stats_url': url,
                         'name': {'$exists': True},
                         'traditional': {'$exists': True},
                         'advanced': {'$exists': True},
                         'misc': {'$exists': True},
                         'scoring': {'$exists': True},
                         'usage': {'$exists': True}}) != 0:
        print('this player already exists in my database', url)
        return

    time.sleep(2)
    driver.implicitly_wait(15)
    driver.get(url)
    player_stats = {
        "name": driver.find_element_by_xpath("//a[@itemtype='http://schema.org/Person']").text,
        "stats_url": url,
    }
    splits = ["traditional", "advanced", "misc", "scoring", "usage"]
    splits_index = 0

    for div in driver.find_elements_by_xpath("//div[@class='nba-stat-table__overflow']"):
        headers = []
        for th in div.find_elements_by_xpath('.//th'):
            headers.append(th.text)
        # print(headers)

        rows = []
        head_index = 0
        for td in div.find_elements_by_xpath(".//tr[@index='0']/td"):
            rows.append({
                "key": headers[head_index],
                "value": td.text,
            })
            head_index += 1
        # print(rows)

        player_stats[splits[splits_index]] = rows
        splits_index += 1

    # print(player_stats)
    if len(player_stats) > 2:
        print('complete one player: ', driver.title, url)
        collection.replace_one(
            {'stats_url': url},
            player_stats,
            upsert=True
        )


if __name__ == '__main__':
    # get_salaries()
    get_stats_of_all_players()

    complete_count = db['stats'].count(
        {
            'name': {'$exists': True},
            'traditional': {'$exists': True},
            'advanced': {'$exists': True},
            'misc': {'$exists': True},
            'scoring': {'$exists': True},
            'usage': {'$exists': True}
        }
    )
    print(complete_count)
