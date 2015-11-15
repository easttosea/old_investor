# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
import urllib
import re
import pandas as pd


def get_fund_info():
    url = 'http://www.abcfund.cn/style/home.php?style=0'
    text = urllib.request.urlopen(url, timeout=10).read()
    text = text.decode('GBK')
    reg = re.compile(r'<tr.*?><td>(.*?)</td></tr>')
    data = reg.findall(text)
    data_list = []
#    for index, row in enumerate(data):
    for row in data:
        if len(row)>1:
            data_list.append([cell for cell in row.split('</td><td>')])
    data_frame = pd.DataFrame(data_list, columns=['mother_code', 'mother_name', 'establish_date', 'list_date',
                                                  'a_code', 'a_name', 'b_code', 'b_name', 'ratio',
                                                  'delist_date', 'annual_yield', 'index_code', 'index_name'])
#    ls = [cls for cls in df.columns if '_v' in cls]
#    for txt in ls:
#        df[txt] = df[txt].map(lambda x : x[:-2])
    ratio_list = []
    a_in_10_list = []
    for ratio in data_frame['ratio']:
        ratio = ratio[-3:]
        if ratio == '1:1':
            ratio = '5:5'
        ratio_list.append(ratio)
        a_in_10 = int(ratio[0:1])
        a_in_10_list.append(a_in_10)

    data_frame['ratio'] = ratio_list
    data_frame.insert(9,'a_in_10',a_in_10_list)
    print(data_frame)
    #data_frame['ratio'] = data_frame['ratio'].map(lambda x : x[-3:]).map('5:5')
    #data_frame['ratio']
    engine = create_engine('sqlite:///fund.db', echo=True)
    data_frame.to_sql('structured_fund_info', engine, if_exists='append')




if __name__ == '__main__':
    print(get_fund_info())

