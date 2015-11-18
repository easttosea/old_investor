# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
import logging
import urllib
import re
import pandas as pd
import datetime
import tushare as ts


def get_fund_info():
    # 1. Get the basic info
    url = 'http://www.abcfund.cn/style/home.php?style=0'
    text = urllib.request.urlopen(url, timeout=10).read()
    text = text.decode('GBK')
    reg = re.compile(r'<tr.*?><td>(.*?)</td></tr>')
    data = reg.findall(text)
    data_list = []
    for row in data:
        if len(row) > 1 and row[0] != '-':
            data_list.append([cell for cell in row.split('</td><td>')])
    data_frame_1 = pd.DataFrame(data_list, columns=['mother_code', 'mother_name', 'establish_date', 'list_date',
                                                    'a_code', 'a_name', 'b_code', 'b_name', 'ratio',
                                                    'delist_date', 'current_annual_rate', 'index_code',
                                                    'index_name'])
    data_frame_1 = data_frame_1.set_index('mother_code')
    data_frame_1['establish_date'] = [_str_to_datetime(dt_str, '%Y-%m-%d')
                                      for dt_str in data_frame_1['establish_date']]
    data_frame_1['list_date'] = [_str_to_datetime(dt_str, '%Y-%m-%d') for dt_str in data_frame_1['list_date']]
    data_frame_1['delist_date'] = [_str_to_datetime(dt_str, '%Y-%m-%d')
                                   for dt_str in data_frame_1['delist_date']]
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
    # Extract the useful strings of current_annual_rate and rate_rule
    current_annual_rate_list = []
    rate_rule_list = []
    reg = re.compile('\+\d%')
    for cell in data_frame_1['current_annual_rate']:
        data = cell.split('<br><font color=#696969>')
        if len(data) > 1:
            current_annual_rate = data[0]
            rate_rule = data[1][:-7]
            if rate_rule == '固定':
                rate_rule = data[0]
            if rate_rule[:2] == '1年':
                rate_rule = rate_rule[2:]
                if reg.match(rate_rule):
                    rate_rule = rate_rule[:-1] + '.0%'
        else:
            current_annual_rate = '-'
            rate_rule = data[0][:2]
            # The data of fund '163109-150022-150023' i crawl from abcfund is wrong, so i correct it myself.
            if rate_rule == '6%':
                current_annual_rate = '5.75%'
                rate_rule = '+3.0%'
        current_annual_rate_list.append(current_annual_rate)
        rate_rule_list.append(rate_rule)
    data_frame_1['current_annual_rate'] = current_annual_rate_list
    data_frame_1.insert(11, 'rate_rule', rate_rule_list)
    # Get the one-year deposit rate
    deposit_name, deposit_rate = ts.get_deposit_rate().loc[6, ['deposit_type', 'rate']]
    if deposit_name == '定期存款整存整取(一年)':
        deposit_rate = float(deposit_rate)
    else:
        logging.error('Failure in getting deposit rate!')
        deposit_rate = 1.5
    # Convert the format of current annual rate from string to number, then calculate the next annual rate, and make
    # both formats 'string' and 'number' of it
    data_frame_1.insert(11, 'num_current_annual_rate', [_str_to_float(n_str[:-1], multiplier=0.01)
                                                        for n_str in data_frame_1['current_annual_rate']])
    data_frame_1.insert(13, 'num_next_annual_rate', [_calculate_next_annual_rate(rate_rule, deposit_rate)
                                                     for rate_rule in data_frame_1['rate_rule']])
    data_frame_1.insert(13, 'next_annual_rate', [_float_to_str(n_float, multiplier=100, append='%')
                                                 for n_float in data_frame_1['num_next_annual_rate']])
    # 2. Get the info of rate adjustment
    url = 'http://www.abcfund.cn/data/arateadjustment.php'
    text = urllib.request.urlopen(url, timeout=10).read()
    text = text.decode('GBK')
    reg = re.compile(r'<tr.*?><td>(.*?)</td></tr>')
    data = reg.findall(text)
    data_list = []
    for row in data:
        if len(row) > 1 and row[0] != '-':
            data_list.append([cell for cell in row.split('</td><td>')])
    data_frame_2 = pd.DataFrame(data_list, columns=['mother_code', 'mother_name', 'rate_adjustment_condition',
                                                    'next_rate_adjustment_date'])
    data_frame_2 = data_frame_2.drop('mother_name', axis=1)
    data_frame_2 = data_frame_2.set_index('mother_code')
    data_frame_2['next_rate_adjustment_date'] = [_str_to_datetime(dt_str, '%Y-%m-%d')
                                                 for dt_str in data_frame_2['next_rate_adjustment_date']]
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

    # 3. Get the conversion condition
    url = 'http://www.abcfund.cn/data/zsinfo.php'
    text = urllib.request.urlopen(url, timeout=10).read()
    text = text.decode('GBK')
    reg = re.compile(r'onclick.*?><td>(.*?)</td><tr')
    data = reg.findall(text)
    data_list = []
    for row in data:
        if len(row) > 1 and row[0] != '-':
            data_list.append([cell for cell in row.replace('</td><td>', '<td>').split('<td>')])
    data_frame_3 = pd.DataFrame(data_list, columns=['mother_code', 'mother_name',
                                                    'next_regular_conversion_date', 'days from now on',
                                                    'ascending_conversion_condition',
                                                    'descending_conversion_condition'])
    data_frame_3 = data_frame_3.drop(['mother_name', 'days from now on'], axis=1)
    data_frame_3 = data_frame_3.set_index('mother_code')
    data_frame_3['next_regular_conversion_date'] = [_str_to_datetime(dt_str, '%Y年%m月%d日')
                                                    for dt_str in data_frame_3['next_regular_conversion_date']]
    # Extract the values of conversion condition
    ascending_conversion_condition_list = []
    for cell in data_frame_3['ascending_conversion_condition']:
        if cell == '-':
            ascending_conversion_condition = 0
        else:
            ascending_conversion_condition = float(cell[7:])
        ascending_conversion_condition_list.append(ascending_conversion_condition)
    data_frame_3['ascending_conversion_condition'] = ascending_conversion_condition_list
    descending_conversion_condition_list = []
    for cell in data_frame_3['descending_conversion_condition']:
        if cell == '-':
            descending_conversion_condition = 0
        elif cell[0] == 'B':
            descending_conversion_condition = float(cell[6:])
        else:
            descending_conversion_condition = float(cell[7:]) * (-1)
        descending_conversion_condition_list.append(descending_conversion_condition)
    data_frame_3['descending_conversion_condition'] = descending_conversion_condition_list

    # 4. Get the net value of mother fund, a and b
    url = 'http://www.abcfund.cn/data/premium.php'
    text = urllib.request.urlopen(url, timeout=10).read()
    text = text.decode('GBK')
    reg = re.compile(r'<tr.*?><td>(.*?)</td></tr>')
    data = reg.findall(text)
    data_list = []
    for row in data:
        if len(row) > 1 and '-</td>' not in row:
            data_list.append([cell for cell in row.split('</td><td>')])
    data_frame_4 = pd.DataFrame(data_list, columns=['mother_code', 'mother_name', 'mother_net_value', 'a_code',
                                                    'a_name', 'a_net_value', 'a_price', 'a_premium', 'a_volume',
                                                    'b_code', 'b_name', 'b_net_value', 'b_price', 'b_premium',
                                                    'b_volume', 'whole_volume'])
    data_frame_4 = data_frame_4.drop(['mother_name', 'a_code', 'a_name', 'a_price', 'a_premium', 'a_volume',
                                      'b_code', 'b_name', 'b_price', 'b_premium', 'b_volume', 'whole_volume'
                                      ], axis=1)
    data_frame_4 = data_frame_4.set_index('mother_code')
    data_frame_4['mother_net_value'] = data_frame_4['mother_net_value'].map(float)
    data_frame_4['a_net_value'] = data_frame_4['a_net_value'].map(float)
    data_frame_4['b_net_value'] = data_frame_4['b_net_value'].map(float)

    # 4. Join the data frames together
    data_frame = data_frame_1.join([data_frame_2, data_frame_3, data_frame_4])

    # 5. Save the data into sqlite database
    engine = create_engine('sqlite:///fund.db', echo=True)
    data_frame.to_sql('structured_fund_info', engine, if_exists='append')


def _str_to_datetime(dt_str, dt_format):
    # Convert format 'string' to 'datetime'
    try:
        dt_datetime = datetime.datetime.strptime(dt_str, dt_format)
    except ValueError:
        dt_datetime = None
    return dt_datetime


def _str_to_float(n_str, multiplier=1):
    try:
        n_num = float(n_str) * multiplier
    except ValueError:
        n_num = 0
    return n_num


def _calculate_next_annual_rate(rate_rule, deposit_rate):
    if '+' in rate_rule:
        return deposit_rate / 100 + float(rate_rule[1:-1]) / 100
    elif rate_rule == '特殊':
        return 0
    else:
        return float(rate_rule[:-1]) / 100


def _float_to_str(n_float, multiplier=1, append=''):
    if n_float == 0:
        return '-'
    else:
        return str(n_float * multiplier) + append


if __name__ == '__main__':
    print(get_fund_info())
