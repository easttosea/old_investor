import sqlite3


structure_fund = {}


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


def init_fund_info():
    conn = sqlite3.connect('../data/fund.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM structured_fund_info')
    table = cursor.fetchall()
    for row in table:
        structure_fund[row[0]] = StructuredFund(row)
        structure_fund[row[4]] = structure_fund[row[0]]
        structure_fund[row[6]] = structure_fund[row[0]]
    cursor.close()
    conn.close()


if __name__ == '__main__':
    init_fund_info()