# -*- coding: utf-8 -*-

import re
import socket
import datetime
import urllib
import sqlite3
import pandas as pd
from sqlalchemy import create_engine
import tushare as ts
import logging
logging.basicConfig(level=logging.INFO)


class StructuredFund(object):
    """The structured fund here."""

    def __init__(self):
        self.TODAY_DATE = datetime.date.today()
        self.MANUAL_CORRECT_RATE = {'163109': [0.0575, '1年+3.0%'], '161719': [0.055, '3年+1.25%'],
                                    '162215': [0.0358, '国债×1.3']}
        self.net_value_date = ''
        self.frame_info = None

        self.fund_a_code = []
        self.fund_b_code = []
        self.i_code = []
        self.frame_realtime = None
        self.update_time = ''

    def init_fund_info(self):
        """Init the info of the structured fund."""
        # 1. Get the basic info.
        url = 'http://www.abcfund.cn/style/fundlist.php'
        reg_ex = r'<tr.*?><td>(.*?)</td></tr>'
        split_str = '</td><td>'
        data_list = web_crawler(url, reg_ex, split_str)
        frame_info_1 = pd.DataFrame(data_list, columns=[
            'm_code', 'm_name', 'establish_date', 'list_date', 'a_code', 'a_name', 'b_code',
            'b_name', 'a_to_b', 'delist_date', 'current_annual_rate', 'i_code', 'i_name'])
        frame_info_1 = frame_info_1[frame_info_1.a_code.str.contains(r'15|50')]
        frame_info_1 = frame_info_1.set_index('m_code')
        # 2. Get the info of rate adjustment.
        url = 'http://www.abcfund.cn/data/arateadjustment.php'
        reg_ex = r'<tr.*?><td>(.*?)</td></tr>'
        split_str = '</td><td>'
        data_list = web_crawler(url, reg_ex, split_str)
        frame_info_2 = pd.DataFrame(data_list, columns=[
            'm_code', 'm_name', 'rate_adjustment_condition', 'next_rate_adjustment_date'])
        frame_info_2 = frame_info_2.drop('m_name', axis=1)
        frame_info_2 = frame_info_2.set_index('m_code')
        # 3. Get the conversion condition.
        url = 'http://www.abcfund.cn/data/zsinfo.php'
        reg_ex = r'onclick.*?><td>(.*?)</td><tr'
        replace_str = '</td><td>'
        split_str = '<td>'
        data_list = web_crawler(url, reg_ex, split_str, replace_str)
        frame_info_3 = pd.DataFrame(data_list, columns=[
            'm_code', 'm_name', 'next_regular_conversion_date', 'days_to_next_regular_conversion_date',
            'ascending_conversion_condition', 'descending_conversion_condition'])
        frame_info_3 = frame_info_3.drop('m_name', axis=1)
        frame_info_3 = frame_info_3.set_index('m_code')
        # 4. Get the net value of m fund, a and b.
        url = 'http://www.abcfund.cn/data/premium.php'
        reg_ex = r'<tr.*?><td>(.*?)</td></tr>'
        split_str = '</td><td>'
        # Get the date of the data of net value.
        reg_ex_date = r'\d{4}年\d{1,2}月\d{1,2}日'
        data_list, date = web_crawler(url, reg_ex, split_str, reg_ex_2=reg_ex_date)
        self.net_value_date = datetime.datetime.strptime(date[0], '%Y年%m月%d日').date()
        frame_info_4 = pd.DataFrame(data_list, columns=[
            'm_code', 'm_name', 'm_net_value', 'a_code', 'a_name', 'a_net_value',
            'a_price', 'a_premium', 'a_volume', 'b_code', 'b_name', 'b_net_value', 'b_price', 'b_premium',
            'b_volume', 'whole_premium'])
        frame_info_4 = frame_info_4.loc[:, ['m_code', 'm_net_value', 'a_net_value', 'b_net_value']]
        frame_info_4 = frame_info_4.set_index('m_code')
        # 5. Join the data frames together.
        self.frame_info = frame_info_1.join([frame_info_2, frame_info_3, frame_info_4], how='inner')

        # Get the one-year deposit rate
        deposit_name, deposit_rate = ts.get_deposit_rate().loc[6, ['deposit_type', 'rate']]
        if deposit_name == '定期存款整存整取(一年)':
            deposit_rate = float(deposit_rate) / 100
        else:
            logging.error('Failure in getting deposit rate!')
            deposit_rate = 1.5 / 100
        # Format the data of table
        establish_date_column = []
        list_date_column = []
        delist_date_column = []
        years_to_delist_date_column = []
        a_in_10_column = []
        a_to_b_column = []
        current_annual_rate_column = []
        rate_rule_column = []
        next_annual_rate_column = []
        next_rate_adjustment_date_column = []
        days_to_next_rate_adjustment_date_column = []
        rate_adjustment_condition_column = []
        next_regular_conversion_date_column = []
        ascending_conversion_condition_column = []
        descending_conversion_condition_column = []
        a_net_value_column = []
        b_net_value_column = []
        m_net_value_column = []
        for index in self.frame_info.index:
            fund = self.frame_info.loc[index, :]
            try:
                establish_date = datetime.datetime.strptime(fund.establish_date, '%Y-%m-%d').date()
            except ValueError:
                establish_date = None
            try:
                list_date = datetime.datetime.strptime(fund.list_date, '%Y-%m-%d').date()
            except ValueError:
                list_date = None
            try:
                delist_date = datetime.datetime.strptime(fund.delist_date, '%Y-%m-%d').date()
            except ValueError:
                delist_date = None
            try:
                years_to_delist_date = (delist_date - self.TODAY_DATE).days / 365
            except TypeError:
                years_to_delist_date = None
            a_in_10 = (int(fund.a_to_b[-3:-2]) / (int(fund.a_to_b[-3:-2]) + int(fund.a_to_b[-1:]))) * 10
            a_to_b = '{0}:{1}'.format(int(a_in_10), int(10-a_in_10))
            rate_and_rule = fund.current_annual_rate.split('<br><font color=#696969>')
            if index in self.MANUAL_CORRECT_RATE:
                current_annual_rate, rate_rule = self.MANUAL_CORRECT_RATE[index]
            elif len(rate_and_rule) > 1:
                current_annual_rate = float(rate_and_rule[0][:-1]) / 100
                rate_rule = rate_and_rule[1][:-7]
                if rate_rule == '固定':
                    rate_rule = '固定' + rate_and_rule[0]
                if '.' not in rate_rule:
                    rate_rule = rate_rule[:-1] + '.0%'
            else:
                current_annual_rate = None
                rate_rule = rate_and_rule[0]
            if '1年+' in rate_rule:
                next_annual_rate = deposit_rate + float(rate_rule[3:-1]) / 100
            elif '3年+' in rate_rule:
                next_annual_rate = 2.75 / 100 + float(rate_rule[3:-1]) / 100
            elif '固定' in rate_rule:
                next_annual_rate = float(rate_rule[2:-1]) / 100
            elif rate_rule == '特殊情况':
                next_annual_rate = None
            else:
                # This is the rate of mother code '162215'
                next_annual_rate = 0.0358
            try:
                next_rate_adjustment_date = datetime.datetime.strptime(
                    fund.next_rate_adjustment_date, '%Y-%m-%d').date()
            except ValueError:
                next_rate_adjustment_date = None
            try:
                days_to_next_rate_adjustment_date = (next_rate_adjustment_date - self.TODAY_DATE).days
            except TypeError:
                days_to_next_rate_adjustment_date = None
            if '动态调整' in fund.rate_adjustment_condition:
                rate_adjustment_condition = '动态调整'
            elif '不定期' in fund.rate_adjustment_condition:
                rate_adjustment_condition = '折算调整'
            elif '不调整' in fund.rate_adjustment_condition:
                rate_adjustment_condition = '不调整'
            else:
                rate_adjustment_condition = '定期调整'
            try:
                next_regular_conversion_date = datetime.datetime.strptime(
                    fund.next_regular_conversion_date, '%Y年%m月%d日').date()
            except ValueError:
                next_regular_conversion_date = None
            if fund.ascending_conversion_condition[0] == '母':
                ascending_conversion_condition = float(fund.ascending_conversion_condition[7:])
            elif fund.ascending_conversion_condition[0] == 'B':
                ascending_conversion_condition = float(fund.ascending_conversion_condition[6:]) * (-1)
            else:
                ascending_conversion_condition = None
            if fund.descending_conversion_condition[0] == 'B':
                descending_conversion_condition = float(fund.descending_conversion_condition[6:])
            elif fund.descending_conversion_condition[0] == '母':
                descending_conversion_condition = float(fund.descending_conversion_condition[7:]) * (-1)
            else:
                descending_conversion_condition = None
            a_net_value = float(fund.a_net_value)
            b_net_value = float(fund.b_net_value)
            try:
                m_net_value = float(fund.m_net_value)
            except ValueError:
                m_net_value = (a_net_value * a_in_10 + b_net_value * (10 - a_in_10)) / 10
            establish_date_column.append(establish_date)
            list_date_column.append(list_date)
            years_to_delist_date_column.append(years_to_delist_date)
            delist_date_column.append(delist_date)
            a_in_10_column.append(a_in_10)
            a_to_b_column.append(a_to_b)
            current_annual_rate_column.append(current_annual_rate)
            rate_rule_column.append(rate_rule)
            next_annual_rate_column.append(next_annual_rate)
            next_rate_adjustment_date_column.append(next_rate_adjustment_date)
            days_to_next_rate_adjustment_date_column.append(days_to_next_rate_adjustment_date)
            rate_adjustment_condition_column.append(rate_adjustment_condition)
            next_regular_conversion_date_column.append(next_regular_conversion_date)
            ascending_conversion_condition_column.append(ascending_conversion_condition)
            descending_conversion_condition_column.append(descending_conversion_condition)
            a_net_value_column.append(a_net_value)
            b_net_value_column.append(b_net_value)
            m_net_value_column.append(m_net_value)
        self.frame_info['establish_date'] = establish_date_column
        self.frame_info['list_date'] = list_date_column
        self.frame_info['delist_date'] = delist_date_column
        self.frame_info['years_to_delist_date'] = years_to_delist_date_column
        self.frame_info['a_in_10'] = a_in_10_column
        self.frame_info['a_to_b'] = a_to_b_column
        self.frame_info['current_annual_rate'] = current_annual_rate_column
        self.frame_info['rate_rule'] = rate_rule_column
        self.frame_info['next_annual_rate'] = next_annual_rate_column
        self.frame_info['next_rate_adjustment_date'] = next_rate_adjustment_date_column
        self.frame_info['days_to_next_rate_adjustment_date'] = days_to_next_rate_adjustment_date_column
        self.frame_info['rate_adjustment_condition'] = rate_adjustment_condition_column
        self.frame_info['next_regular_conversion_date'] = next_regular_conversion_date_column
        self.frame_info['ascending_conversion_condition'] = ascending_conversion_condition_column
        self.frame_info['descending_conversion_condition'] = descending_conversion_condition_column
        self.frame_info['a_net_value'] = a_net_value_column
        self.frame_info['b_net_value'] = b_net_value_column
        self.frame_info['m_net_value'] = m_net_value_column

        # 5. Save the data into csv file
        self.frame_info.to_csv('../data/structured_fund_info.csv')

    def init_fund_code(self):
        self.fund_a_code = list(self.frame_info['a_code'].values)
        self.fund_b_code = list(self.frame_info['b_code'].values)
        self.i_code = []
        for code in list(set(list(self.frame_info['i_code']))):
            if code[0:3] == '399':
                self.i_code.append(code)

    def update_realtime_quotations(self):
        # 1. Update the data of fund_a
        frame_realtime_a = _realtime_quotations(self.fund_a_code)
        update_time = frame_realtime_a.iat[0, -1]
        if self.update_time != update_time:
            self.update_time = update_time
            frame_realtime_a.columns = [
                'a_name', 'a_price', 'a_volume', 'a_amount', 'a_b1_p', 'a_b1_v', 'a_b2_p', 'a_b2_v',
                'a_b3_p', 'a_b3_v', 'a_b4_p', 'a_b4_v', 'a_b5_p', 'a_b5_v', 'a_a1_p', 'a_a1_v', 'a_a2_p',
                'a_a2_v', 'a_a3_p', 'a_a3_v', 'a_a4_p', 'a_a4_v', 'a_a5_p', 'a_a5_v', 'a_high', 'a_low',
                'a_pre_close', 'a_open', 'a_date', 'a_time']
            for index in frame_realtime_a[frame_realtime_a.a_volume == 0].index:
                frame_realtime_a.at[index, 'a_price'] = frame_realtime_a.at[index, 'a_pre_close']
            frame_realtime_a = frame_realtime_a.drop('a_name', axis=1)
            self.frame_realtime = self.frame_info.join(frame_realtime_a, on='a_code', how='inner')
            self.frame_realtime['a_increase_value'] = self.frame_realtime['a_price'] - self.frame_realtime[
                'a_pre_close']
            self.frame_realtime['a_increase_rate'] = self.frame_realtime[
                                                         'a_increase_value'] / self.frame_realtime['a_pre_close']
            self.frame_realtime['a_premium_rate'] = (self.frame_realtime['a_price'] - self.frame_realtime[
                'a_net_value']) / self.frame_realtime['a_net_value']
            self.frame_realtime['modified_rate_of_return'] = self.frame_realtime['next_annual_rate'] / (
                self.frame_realtime['a_price'] - (self.frame_realtime['a_net_value'] - 1) +
                self.frame_realtime['days_to_next_rate_adjustment_date'] / 365 *
                (self.frame_realtime['next_annual_rate'] - self.frame_realtime['current_annual_rate']))

            # 2. update the data of the increase rate of index
            frame_realtime_i = _realtime_quotations(self.i_code)
            frame_realtime_i['i_increase_rate'] = (frame_realtime_i['price'] - frame_realtime_i[
                'pre_close']) / frame_realtime_i['pre_close']
            frame_realtime_i = frame_realtime_i.loc[:, ['i_increase_rate']]
            self.frame_realtime = self.frame_realtime.join(frame_realtime_i, on='i_code')

            # 3. Calculate the distance of irregular conversion
            m_descending_distance_list = []
            for code in self.frame_realtime.index:
                fund = self.frame_realtime.loc[code, ['m_net_value', 'a_net_value', 'a_date',
                                               'i_increase_rate', 'descending_conversion_condition']]
                if fund.isnull().i_increase_rate or self.net_value_date == fund.a_date:
                    m_price = fund.m_net_value
                else:
                    m_price = fund.m_net_value * (1 + fund.i_increase_rate * 0.95)
                if fund.descending_conversion_condition == 0:
                    m_descending_distance = None
                else:
                    if fund.descending_conversion_condition > 0:
                        m_descending_conversion_condition = (fund.descending_conversion_condition + fund.a_net_value)/2
                    else:
                        m_descending_conversion_condition = fund.descending_conversion_condition * (-1)
                    m_descending_distance = (m_price - m_descending_conversion_condition) / m_price
                m_descending_distance_list.append(m_descending_distance)
            self.frame_realtime['m_descending_distance'] = m_descending_distance_list
            # Write into SQLite
            self.frame_realtime.to_csv('../data/structured_fund_a_csv')
            return True
        else:
            return False


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
    data_frame['date'] = [_format_convert(cell, 'date', source_format='%Y-%m-%d') for cell in data_frame['date']]
    return data_frame


def web_crawler(url, reg_ex, split_str, replace_str=None, reg_ex_2=None, time_out=10):
    """Crawl from a website, and extract the data into a list.

    Args:
        url: The url of website.
        reg_ex: The regular expression for extracting the data from text.
        split_str: The funds are split by the string of split_str.
        replace_str: When the website text is not standard, the replace_str should be replaced to split_str.
        reg_ex_2: The extra regular expression.
        time_out: The time limit of urlopen.

    Returns:
        A list of row data fetched. Each row is a list of strings. For example:
        [['161022', '富国创业板指数分级', '150152', '创业板A', ...]
         ['164705', '汇添富恒生指数分级', '150169', '恒生A', ...]
         ...]
        If reg_ex_2 exists, return an extra list of data fetched, but this is not split.
    """
    try:
        with urllib.request.urlopen(url, timeout=time_out) as f:
            text = f.read()
    except socket.timeout:
        logging.info('Timeout when loading this url: {0}'.format(url))
        return web_crawler(url, reg_ex, split_str, replace_str, time_out)
    except socket.error:
        logging.info('Socket error when loading this url: {0}'.format(url))
        return web_crawler(url, reg_ex, split_str, replace_str, time_out)
    text = text.decode('GBK')
    reg = re.compile(reg_ex)
    data = reg.findall(text)
    data_list = []
    if replace_str is not None:
        for row in data:
            if len(row) > 1:
                data_list.append([cell for cell in row.replace(replace_str, split_str).split(split_str)])
    else:
        for row in data:
            if len(row) > 1:
                data_list.append([cell for cell in row.split(split_str)])
    if reg_ex_2 is None:
        return data_list
    else:
        data_2 = re.findall(reg_ex_2, text)
        return data_list, data_2



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
