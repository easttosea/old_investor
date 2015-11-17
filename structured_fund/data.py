import sqlite3


class structured_fund(object):
    def __init__(self, mother_code):
        self.mother_code = mother_code
        self.mother_name = ''
        self.establish_date = None
        self.list_date = None



conn = sqlite3.connect('../data/fund.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM structured_fund_info')
values = cursor.fetchall()
print(values)
cursor.close()
conn.close()