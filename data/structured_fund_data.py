# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
import urllib
import re
import pandas as pd


def get_fund_info():
    # 1. Get the basic info
    url = 'http://www.abcfund.cn/style/home.php?style=0'
    text = urllib.request.urlopen(url, timeout=10).read()
    text = text.decode('GBK')
    reg = re.compile(r'<tr.*?><td>(.*?)</td></tr>')
    data = reg.findall(text)
    data_list = []
    for row in data:
        if len(row)>1:
            data_list.append([cell for cell in row.split('</td><td>')])
    data_frame_1 = pd.DataFrame(data_list, columns=['mother_code', 'mother_name', 'establish_date', 'list_date',
                                                    'a_code', 'a_name', 'b_code', 'b_name', 'ratio',
                                                    'delist_date', 'annual_rate', 'index_code', 'index_name'])
    data_frame_1 = data_frame_1.set_index('mother_code')
    # Extract the useful strings of ratio, and get the ratio of a in 10
    ratio_list = []
    a_in_10_list = []
    for cell in data_frame_1['ratio']:
        ratio = cell[-3:]
        if ratio == '1:1':
            ratio = '5:5'
        ratio_list.append(ratio)
        a_in_10 = int(ratio[0:1])
        a_in_10_list.append(a_in_10)
    data_frame_1['ratio'] = ratio_list
    data_frame_1.insert(8, 'a_in_10', a_in_10_list)
    # Extract the useful strings of annual_rate and rate_rule
    annual_rate_list = []
    rate_rule_list = []
    reg = re.compile('\+\d%')
    for cell in data_frame_1['annual_rate']:
        data = cell.split('<br><font color=#696969>')
        if len(data) > 1:
            annual_rate = data[0]
            rate_rule = data[1][:-7]
            if rate_rule[:2] == '1年':
                rate_rule = rate_rule[2:]
                if reg.match(rate_rule):
                    rate_rule = rate_rule[:-1] + '.0%'
        else:
            annual_rate = ''
            rate_rule = data[0]
            # The data of fund '163109-150022-150023' i crawl from abcfund is wrong, so i correct it myself.
            if rate_rule == '6%':
                annual_rate = '5.75%'
                rate_rule = '+3.0%'
        annual_rate_list.append(annual_rate)
        rate_rule_list.append(rate_rule)
    data_frame_1['annual_rate'] = annual_rate_list
    data_frame_1.insert(11, 'rate_rule', rate_rule_list)

    # 2. Get the info of rate adjustment
    url = 'http://www.abcfund.cn/data/arateadjustment.php'
    text = urllib.request.urlopen(url, timeout=10).read()
    text = text.decode('GBK')
    reg = re.compile(r'<tr.*?><td>(.*?)</td></tr>')
    data = reg.findall(text)
    data_list = []
    for row in data:
        if len(row)>1:
            data_list.append([cell for cell in row.split('</td><td>')])
    data_frame_2 = pd.DataFrame(data_list, columns=['mother_code', 'mother_name', 'rate_adjustment_condition',
                                                    'next_rate_adjustment_date'])
    data_frame_2 = data_frame_2.drop('mother_name', axis=1)
    data_frame_2 = data_frame_2.set_index('mother_code')
    # Classify the rate adjustment condition
    rate_adjustment_condition_list = []
    for cell in data_frame_2['rate_adjustment_condition']:
        if '动态调整' in cell:
            rate_adjustment_condition = '动态调整'
        elif '不定期' in cell:
            rate_adjustment_condition = '不定期调整'
        elif '不调整' in cell:
            rate_adjustment_condition = '不调整'
        else:
            rate_adjustment_condition = '定期调整'
        rate_adjustment_condition_list.append(rate_adjustment_condition)
    data_frame_2['rate_adjustment_condition'] = rate_adjustment_condition_list

    # Join the data frames together
    data_frame = data_frame_1.join(data_frame_2)
    # Save the data into sqlite database
    engine = create_engine('sqlite:///fund.db', echo=True)
    data_frame.to_sql('structured_fund_info', engine, if_exists='append')


if __name__ == '__main__':
    print(get_fund_info())

