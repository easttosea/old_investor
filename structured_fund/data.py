import sqlite3
import tushare as ts


structure_fund_mother = {}
structure_fund_a = {}
structure_fund_b = {}


class StructuredFund(object):
    def __init__(self, values):
        self.mother_code = values[0]
        self.mother_name = values[1]
        self.establish_date = values[2]
        self.list_date = values[3]
        self.a_code = values[4]
        self.a_name = values[5]
        self.b_code = values[6]
        self.b_name = values[7]
        self.ratio = values[8]
        self.a_in_10 = values[9]
        self.delist_date = values[10]
        self.current_annual_rate = values[11]
        self.num_current_annual_rate = values[12]
        self.rate_rule = values[13]
        self.next_annual_rate = values[14]
        self.num_next_annual_rate = values[15]
        self.index_code = values[16]
        self.index_name = values[17]
        self.rate_adjustment_condition = values[18]
        self.next_rate_adjustment_date = values[19]
        self.next_regular_conversion_date = values[20]
        self.ascending_conversion_condition = values[21]
        self.descending_conversion_condition = values[22]
        self.mother_net_value = values[23]
        self.a_net_value = values[24]
        self.b_net_value = values[25]
        self.a_price = 0
        self.a_increase_percentage = 0
        self.a_increase_value = 0
        self.a_volume = 0
        self.a_amount = 0
        self.a_bid = 0
        self.a_b1_v = 0
        self.a_ask = 0
        self.a_a1_v = 0
        self.a_high = 0
        self.a_low = 0
        self.a_pre_close = 0
        self.a_today_open = 0
        self.a_timestamp = ''
        self.a_premium_rate = 0

    def update_data(self, value):
        self.a_price = float(value[1])
        self.a_volume = int(value[2])
        self.a_amount = float(value[3])
        self.a_bid = float(value[4])
        try:
            self.a_b1_v = int(value[5])
        except ValueError:
            self.a_b1_v = 0
        self.a_ask = float(value[6])
        try:
            self.a_a1_v = int(value[7])
        except ValueError:
            self.a_a1_v = 0
        self.a_high = float(value[8])
        self.a_low = float(value[9])
        self.a_pre_close = float(value[10])
        self.a_today_open = float(value[11])
        self.a_timestamp = value[12]
        self.a_increase_value = self.a_price - self.a_pre_close
        self.a_increase_percentage = self.a_increase_value / self.a_pre_close
        self.a_premium_rate = (self.a_price - self.a_net_value) / self.a_net_value

    def format_data(self):
        # The variables are transformed to strings for display
        code = self.code
        name = self.name
        price = str('{0:.3f}'.format(self.price))
        increase_percentage = str('{0:.2f}'.format(self.increase_percentage * 100)) + '%'
        amount = str('{0:.1f}'.format(self.amount / 10000)) + '万'
        bid = str('{0:.3f}'.format(self.bid))
        b1_v = str(self.b1_v)
        ask = str('{0:.3f}'.format(self.ask))
        a1_v = str(self.a1_v)
        high = str('{0:.3f}'.format(self.high))
        low = str('{0:.3f}'.format(self.low))
        pre_close = str('{0:.3f}'.format(self.pre_close))
        today_open = str('{0:.3f}'.format(self.today_open))
        timestamp = self.timestamp
        premium_rate = str('{0:.2f}'.format(self.premium_rate * 100)) + '%'
        net_value = str('{0:.3f}'.format(self.net_value))
#        annual_yield = str('{0:.3f}'.format(self.annual_yield * 100)) + '%'

        return code, name, price, increase_percentage, net_value, premium_rate, amount, ask, a1_v, bid, b1_v, \
            high, low, pre_close, today_open


def format_code_list(symbols):
    # convert code to list, in the format of [['code1', 'code2', ...], ['code31', 'code32', ...], ...]
    if isinstance(symbols, str):
        code_list = [[symbols]]
        return code_list
    else:
        code_list = []
        i = 0
        while i < len(symbols):
            code_list.append(symbols[i:i+30])
            i += 30
        return code_list


def realtime_quotations(code_list):
    # Get realtime quotations, and put them in the list, in the format of [(code1, values), (code2, values2) ... ]
    table = ts.get_realtime_quotes(code_list)[['code', 'name', 'price', 'volume', 'amount', 'bid', 'b1_v',
                                               'ask', 'a1_v', 'high', 'low', 'pre_close', 'open', 'time']]
    return table.values


def init_fund_info():
    conn = sqlite3.connect('../data/fund.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM structured_fund_info WHERE list_date IS NOT NULL')
    table = cursor.fetchall()
    for row in table:
        structure_fund_mother[row[0]] = StructuredFund(row)
        structure_fund_a[row[4]] = structure_fund_mother[row[0]]
        structure_fund_b[row[6]] = structure_fund_mother[row[0]]
    cursor.close()
    conn.close()


def update_realtime_quotations():
    code_a_list_split_30 = format_code_list(structure_fund_a.keys())
    for code_list in code_a_list_split_30:
        table = realtime_quotations(code_list)
        for row in table:
            structure_fund_a[row[0]].update_data(row[2:])


if __name__ == '__main__':
    init_fund_info()
    print(structure_fund_a['150152'].a_net_value)