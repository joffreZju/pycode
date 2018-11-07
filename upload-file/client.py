# coding:utf-8

import requests

# 用 requests 库发起 http post 请求，发送文件
if __name__ == '__main__':
    files = {'file': open('./img-1.png', 'rb')}
    resp = requests.post('http://localhost:8888/service', files=files)
    print(resp.text)
