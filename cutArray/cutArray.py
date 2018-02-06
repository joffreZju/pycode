# coding:utf-8

import pandas as pd


def read_from_excel(filename):
    df = pd.read_excel(filename, sheetname=0, index_col=None)
    long_array = []
    for k, v in enumerate(df['A']):
        long_array.append(v)
    return long_array


def cut_array(filename):
    long_array = read_from_excel(filename)
    print len(long_array)
    # find locations of zero
    location = []
    start, end = 0, 0
    for k, v in enumerate(long_array):
        if v != 0 or k == len(long_array) - 1:
            if end - start + 1 >= 1440:
                location.append(start)
                location.append(end)
            start, end = k + 1, k + 1
        else:
            end += 1

    print location

    # cut the slice except 0
    result = []
    for k, v in enumerate(location):
        if k == 0 and location[k] != 0:
            result.append(long_array[:location[k]])
        elif k == len(location) - 1:
            if location[k] < len(long_array) - 1:
                result.append(long_array[location[k]:])
            break
        if k % 2 != 0:
            result.append(long_array[location[k]: location[k + 1]])

    # log
    print len(result)
    length = 0
    for v in result:
        length += len(v)
    print length

    # write result to excel
    writer = pd.ExcelWriter("./result" + filename)
    for k, v in enumerate(result):
        df = pd.DataFrame(data=v)
        df.to_excel(excel_writer=writer, sheet_name=str(k + 1), encoding="utf-8")
    writer.close()


if __name__ == '__main__':
    cut_array('1.xlsx')
    cut_array('2.xlsx')
    # cut_array('3.xlsx')
