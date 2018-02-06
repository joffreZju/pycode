# -*- coding: utf-8 -*-
import chardet
import re


# 返回传入字符串的编码
def detectPageCharset(text):
    if isinstance(text, str):
        result = chardet.detect(text)
        return result['encoding']
    else:
        return None


# 获取一个完整链接的HomeURL
# http://www.yokamen.cn/auto/cheku/2013/0604089256.shtml?source=brand
# 返回 http://www.yokamen.cn
def getHomeUrl(url):
    pattern = re.compile(r'(http://[\w|\.]+)')
    result = re.search(pattern, url)
    if result is None:
        return None
    home_url = result.group()
    return home_url

def isCompleteUrl(url):
    if url is None:
        return False
    if url.count("http:") != 0:
        return True
    return False

# 集合类型 不想被过滤的URL集合
URL_NO_FILTER = set()
