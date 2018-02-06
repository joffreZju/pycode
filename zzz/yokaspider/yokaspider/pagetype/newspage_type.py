# -*- coding: utf-8 -*-

page_rules = [
    # page type 1
    {'pageform': '//div[@class="contents"]/div[@id="brand-right"]/div[@class="m-zx-lbox"]',
     'title': './h1/text()',
     'date': './dl[@class="date"]/dt/span[1]/text()',
     'content': ['./div[@class="main"]//p//text()'],
     'nextpage': None,
     'allpage': None,
     },
    # page type 2
    {'pageform': '//div[@class="g-content clearfix m-first"]/div[@class="first clearfix"]/div[@class="g-main fleft"]',
     'title': './h1[@class="infoTitle"]/text()',
     'date': './div[@class="infoTime"]/div[@class="time"]/i/text()',
     'content': ['./div[@class="double_quotes"]/div/text()',
                 './div[@class="textCon"]//p//text()'],
     'nextpage': None,
     'allpage': './dl[@class="pages_fullRead"]/dd/a/@href',
     },
    # page type 3
    {'pageform': '//div[@class="g-content clearfix articlePic"]',
     'title': './h1[@id="picTitle"]/text()',
     'date': None,
     'content': ['./dl[@class="text"]//dd/text()'],
     'nextpage': None,
     'allpage': None,
     },
    # page type 4
    {'pageform': '//div[@class="centess"]//div[@id="pardynr"]',
     'title': './dl[@class="viewtis"]/dt/h1/text()',
     'date': './dl[@class="viewtis"]/dd/text()',
     'content': ['./div[@id="viewbody"]//p//text()'],
     'nextpage': './div[@id="viewbody"]//span[@class="pagebox_next"]/a/@href',
     'allpage': None,
     },
    # page type 5
    {'pageform': '//div[@id="content94"]//div[@class="con2_left_row1"]',
     'title': './h2/text()',
     'date': './div[@class="src"]/text()',
     'content': ['./div[@class="con"]//p//text()'],
     'nextpage': './div[@class="con"]/p[@align="right"]/a[position()>1 and @style]/@href',
     'allpage': None,
     },
    # page type 6:
    {'pageform': '//div[starts-with(@class, "yo_content")]//div[@class="infoContent"]',
     'title': './/h1[1]/text()',
     'date': './div[starts-with(@class, "time")]//span[1]//text()',
     'content': ['.//p[starts-with(@class, "lead")]/text()',
                 './div[@class="textCon"]//p//text()'],
     'nextpage': './div[@class="pages"]//a[@class="nextpage"]/@href',
     'allpage': None,
     },
    # page type 7:
    {'pageform': '//div[@class="picBox"]',
     'title': './div[@class="title"]/h1/text()',
     'date': None,
     'content': ['.//p//text()'],
     'nextpage': None,
     'allpage': None,
    },
    # page type 8:
    {'pageform': '//div[@class="centess"]//div[@id="bodydy"]',
     'title': './h1/text()',
     'date': './div[@class="conms"]/text()',
     'content': ['./div[@class="contentbd"]//p//text()'],
     'nextpage': './div[@class="contentbd"]//span[@class="pagebox_next"]/a/@href',
     'allpage': None,
    }
]

class NewsPage(object):
    def __init__(self):
        pass