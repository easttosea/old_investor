# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
import logging
import urllib
import re
import pandas as pd
import datetime
import tushare as ts
import sqlite3


class StructuredFund(object):
    def __init__(self):
        self.fund_a_code = []
        self.fund_b_code = []
        self.frame_info = None
        self.frame_realtime = None
        self.TODAY_DATE = datetime.date.today()

    def init_fund_info(self):
        # 1. Get the basic info
        url = 'http://www.abcfund.cn/style/fundlist.php'
        text = urllib.request.urlopen(url, timeout=10).read()
        text = text.decode('GBK')
        reg = re.compile(r'<tr.*?><td>(.*?)</td></tr>')
        data = reg.findall(text)
        data_list = []
        for row in data:
            if len(row) > 1:
                data_list.append([cell for cell in row.split('</td><td>')])
        frame_info_1 = pd.DataFrame(data_list, columns=['mother_code', 'mother_name', 'establish_date', 'list_date',
                                                        'a_code', 'a_name', 'b_code', 'b_name', 'ratio',
                                                        'delist_date', 'current_annual_rate', 'index_code',
                                                        'index_name'])
        frame_info_1 = frame_info_1[frame_info_1['a_code'].str.contains('15')]
        frame_info_1 = frame_info_1.set_index('mother_code')
        frame_info_1['establish_date'] = [_format_convert(cell, 'date', '%Y-%m-%d') for cell in
                                          frame_info_1['establish_date']]
        frame_info_1['list_date'] = [_format_convert(cell, 'date', '%Y-%m-%d') for cell in
                                     frame_info_1['list_date']]
        frame_info_1['delist_date'] = [_format_convert(cell, 'date', '%Y-%m-%d') for cell in
                                       frame_info_1['delist_date']]
        # Extract the useful strings of ratio, and get the ratio of a in 10
        ratio_list = []
        a_in_10_list = []
        for cell in frame_info_1['ratio']:
            ratio = cell[-3:]
            if ratio == '1:1':
                ratio = '5:5'
            ratio_list.append(ratio)
            a_in_10 = int(ratio[0:1])
            a_in_10_list.append(a_in_10)
        frame_info_1['ratio'] = ratio_list
        frame_info_1['a_in_10'] = a_in_10_list
        # Extract the useful strings of current_annual_rate and rate_rule
        current_annual_rate_list = []
        rate_rule_list = []
        for cell in frame_info_1['current_annual_rate']:
            data = cell.split('<br><font color=#696969>')
            if len(data) > 1:
                current_annual_rate = _format_convert(data[0], 'float_percent')
                rate_rule = data[1][:-7]
                if rate_rule == '固定':
                    rate_rule = '固定' + data[0]
                elif '.' not in rate_rule:
                    rate_rule = rate_rule[:-1] + '.0%'
            else:
                current_annual_rate = 0
                rate_rule = data[0]
            current_annual_rate_list.append(current_annual_rate)
            rate_rule_list.append(rate_rule)
        frame_info_1['current_annual_rate'] = current_annual_rate_list
        frame_info_1['rate_rule'] = rate_rule_list
        manual_change = [('163109', 0.0575, '1年+3.0%'), ('161719', 0.055, '3年+1.25%'),
                         ('162215', 0.0358, '国债*1.3')]
        for code, current_annual_rate, rate_rule in manual_change:
            if code in frame_info_1.index:
                frame_info_1.loc[code, ['current_annual_rate', 'rate_rule']] = (current_annual_rate, rate_rule)
        # Get the one-year deposit rate
        deposit_name, deposit_rate = ts.get_deposit_rate().loc[6, ['deposit_type', 'rate']]
        if deposit_name == '定期存款整存整取(一年)':
            deposit_rate = float(deposit_rate) / 100
        else:
            logging.error('Failure in getting deposit rate!')
            deposit_rate = 1.5 / 100
        # Calculate the next annual rate
        next_annual_rate_list = []
        for cell in frame_info_1['rate_rule']:
            if '1年+' in cell:
                next_annual_rate = deposit_rate + _format_convert(cell[3:], 'float_percent')
            elif '3年+' in cell:
                next_annual_rate = 2.75 / 100 + _format_convert(cell[3:], 'float_percent')
            elif '固定' in cell:
                next_annual_rate = _format_convert(cell[2:], 'float_percent')
            elif cell == '特殊情况':
                next_annual_rate = 0
            else:
                next_annual_rate = 0.0888
            next_annual_rate_list.append(next_annual_rate)
        frame_info_1['next_annual_rate'] = next_annual_rate_list

        # 2. Get the info of rate adjustment
        url = 'http://www.abcfund.cn/data/arateadjustment.php'
        text = urllib.request.urlopen(url, timeout=10).read()
        text = text.decode('GBK')
        reg = re.compile(r'<tr.*?><td>(.*?)</td></tr>')
        data = reg.findall(text)
        data_list = []
        for row in data:
            if len(row) > 1:
                data_list.append([cell for cell in row.split('</td><td>')])
        frame_info_2 = pd.DataFrame(data_list, columns=['mother_code', 'mother_name', 'rate_adjustment_condition',
                                                        'next_rate_adjustment_date'])
        frame_info_2 = frame_info_2.drop('mother_name', axis=1)
        frame_info_2 = frame_info_2.set_index('mother_code')
        frame_info_2['next_rate_adjustment_date'] = [_format_convert(cell, 'datetime', '%Y-%m-%d')
                                                     for cell in frame_info_2['next_rate_adjustment_date']]
        frame_info_2['days_to_next_rate_adjustment'] = [_calculate_minus_days_of_two_dates(
            date.date(), self.TODAY_DATE) for date in frame_info_2['next_rate_adjustment_date']]
        # Classify the rate adjustment condition
        rate_adjustment_condition_list = []
        for cell in frame_info_2['rate_adjustment_condition']:
            if '动态调整' in cell:
                rate_adjustment_condition = '动态调整'
            elif '不定期' in cell:
                rate_adjustment_condition = '不定期调整'
            elif '不调整' in cell:
                rate_adjustment_condition = '不调整'
            else:
                rate_adjustment_condition = '定期调整'
            rate_adjustment_condition_list.append(rate_adjustment_condition)
        frame_info_2['rate_adjustment_condition'] = rate_adjustment_condition_list

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
        frame_info_3 = pd.DataFrame(data_list, columns=['mother_code', 'mother_name',
                                                        'next_regular_conversion_date', 'days from now on',
                                                        'ascending_conversion_condition',
                                                        'descending_conversion_condition'])
        frame_info_3 = frame_info_3.drop(['mother_name', 'days from now on'], axis=1)
        frame_info_3 = frame_info_3.set_index('mother_code')
        frame_info_3['next_regular_conversion_date'] = [_format_convert(cell, 'datetime', '%Y年%m月%d日') for
                                                        cell in frame_info_3['next_regular_conversion_date']]
        # Extract the values of conversion condition
        ascending_conversion_condition_list = []
        for cell in frame_info_3['ascending_conversion_condition']:
            if cell == '-':
                ascending_conversion_condition = 0
            else:
                ascending_conversion_condition = float(cell[7:])
            ascending_conversion_condition_list.append(ascending_conversion_condition)
        frame_info_3['ascending_conversion_condition'] = ascending_conversion_condition_list
        descending_conversion_condition_list = []
        for cell in frame_info_3['descending_conversion_condition']:
            if cell == '-':
                descending_conversion_condition = 0
            elif cell[0] == 'B':
                descending_conversion_condition = float(cell[6:])
            else:
                descending_conversion_condition = float(cell[7:]) * (-1)
            descending_conversion_condition_list.append(descending_conversion_condition)
        frame_info_3['descending_conversion_condition'] = descending_conversion_condition_list

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
        frame_info_4 = pd.DataFrame(data_list, columns=['mother_code', 'mother_name', 'mother_net_value', 'a_code',
                                                        'a_name', 'a_net_value', 'a_price', 'a_premium', 'a_volume',
                                                        'b_code', 'b_name', 'b_net_value', 'b_price', 'b_premium',
                                                        'b_volume', 'whole_volume'])
        frame_info_4 = frame_info_4.drop(['mother_name', 'a_code', 'a_name', 'a_price', 'a_premium', 'a_volume',
                                          'b_code', 'b_name', 'b_price', 'b_premium', 'b_volume', 'whole_volume'
                                          ], axis=1)
        frame_info_4 = frame_info_4.set_index('mother_code')
        frame_info_4['mother_net_value'] = frame_info_4['mother_net_value'].map(float)
        frame_info_4['a_net_value'] = frame_info_4['a_net_value'].map(float)
        frame_info_4['b_net_value'] = frame_info_4['b_net_value'].map(float)

        # 4. Join the data frames together
        self.frame_info = frame_info_1.join([frame_info_2, frame_info_3, frame_info_4])
        self.frame_info = self.frame_info.dropna(how='any', subset=['list_date'])

#        # 5. Save the data into sqlite database
#        engine = create_engine('sqlite:///fund.db')
#        self.frame_info.to_sql('structured_fund_info', engine, if_exists='replace')
#        self.frame_info.to_sql('structured_fund_info', engine, if_exists='replace')

    def init_fund_code(self):
        self.fund_a_code = list(self.frame_info['a_code'].values)
        self.fund_b_code = list(self.frame_info['b_code'].values)

    def update_realtime_quotations(self):
        frame_realtime = _realtime_quotations(self.fund_a_code)
        frame_realtime = self.frame_info.join(frame_realtime, on='a_code', how='inner')
        frame_realtime['a_increase_value'] = frame_realtime['price'] - frame_realtime['pre_close']
        frame_realtime['a_increase_rate'] = frame_realtime['a_increase_value'] / frame_realtime['pre_close']
        frame_realtime['premium_rate'] = (frame_realtime['price'] - frame_realtime['a_net_value']) / frame_realtime['a_net_value']
        frame_realtime['modified_rate_of_return'] = frame_realtime['num_next_annual_rate'] / (
            frame_realtime['price'] - (frame_realtime['a_net_value'] - 1) + frame_realtime['days_to_next_rate_adjustment'] / 365 * (
                frame_realtime['num_next_annual_rate'] - frame_realtime['num_current_annual_rate']))
        self.frame_realtime = frame_realtime
        engine = create_engine('sqlite:///fund.db')
        frame_realtime.to_sql('structured_fund_a', engine, if_exists='replace')

    def output_a(self):
        frame_output = self.frame_realtime[['a_code', 'a_name', 'price', 'a_increase_rate', 'amount', 'a_net_value',
                                    'premium_rate', 'rate_rule', 'current_annual_rate', 'next_annual_rate',
                                     'modified_rate_of_return']]
        for column in ['price', 'a_increase_rate', 'amount', 'a_net_value', 'premium_rate', 'rate_rule',
                       'current_annual_rate', 'next_annual_rate', 'modified_rate_of_return']:
            frame_output[column] = frame_output[column].map(str)
        return list(frame_output.values)


def _format_convert(source_data, target_type, source_format='', decimal=2):
    if target_type == 'int':
        try:
            return int(source_data)
        except ValueError:
            return 0
    elif target_type == 'float':
        try:
            return float(source_data)
        except ValueError:
            return 0.0
    elif target_type == 'date':
        try:
            return datetime.datetime.strptime(source_data, source_format).date()
        except ValueError:
            return None
    elif target_type == 'float_percent':
        try:
            return float(source_data[:-1]) / 100
        except ValueError:
            return 0.0
    elif target_type == 'str_percent':
        if source_data > 0:
            return str(round(source_data * 100, decimal)) + '%'
        else:
            return '-'



def _calculate_minus_days_of_two_dates(first_date, second_date):
    try:
        return (first_date - second_date).days
    except TypeError:
        return -1





def _realtime_quotations(symbols):
    # Get the list split by 30 codes, in the format of [['code1', 'code2', ...], ['code31', 'code32', ...], ...]
    if isinstance(symbols, str):
        code_list = [[symbols]]
    else:
        code_list = []
        i = 0
        while i < len(symbols):
            code_list.append(symbols[i:i+30])
            i += 30
    # Get realtime quotations, in the format of data frame.
    data_frame = pd.DataFrame()
    for code_list_split_30 in code_list:
        table = ts.get_realtime_quotes(code_list_split_30).loc[
            :, ['code', 'name', 'price', 'volume', 'amount', 'b1_p', 'b1_v', 'b2_p', 'b2_v', 'b3_p',
                'b3_v', 'b4_p', 'b4_v', 'b5_p', 'b5_v', 'a1_p', 'a1_v', 'a2_p', 'a2_v', 'a3_p', 'a3_v',
                'a4_p', 'a4_v', 'a5_p', 'a5_v', 'high', 'low', 'pre_close', 'open', 'date', 'time']]
        table = table.set_index('code')
        data_frame = pd.concat([data_frame, table])
    for column in ['volume', 'b1_v', 'b2_v', 'b3_v', 'b4_v', 'b5_v', 'a1_v', 'a2_v', 'a3_v', 'a4_v',
                   'a5_v']:
        data_frame[column] = [_format_convert(cell, 'int') for cell in data_frame[column]]
    for column in ['price', 'amount', 'b1_p', 'b2_p', 'b3_p', 'b4_p', 'b5_p', 'a1_p', 'a2_p', 'a3_p',
                   'a4_p', 'a5_p', 'high', 'low', 'pre_close', 'open']:
        data_frame[column] = [_format_convert(cell, 'float') for cell in data_frame[column]]
    return data_frame


if __name__ == '__main__':
    structured_fund = StructuredFund()
    structured_fund.init_fund_info()
    structured_fund.init_fund_code()
    structured_fund.update_realtime_quotations()
