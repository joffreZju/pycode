# -*- coding: utf-8 -*-

import time
import os

if __name__ == '__main__':
    files = os.listdir('./')
    for file in files:
        if file.find('.bson') > 0:
            os.system('mongorestore --host 10.214.224.142:20000 --db stock_dataset_1 ' + file)
            time.sleep(1)
