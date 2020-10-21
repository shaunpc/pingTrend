# Database.py
#
# performs all actions to support SQLITE database usage
# for PingTrend

import sqlite3
from sqlite3 import Error


class Database:

    def __init__(self, file):
        self.file = file
        self.conn = sqlite3.connect(self.file, isolation_level=None)   # autocommit
        self.cur = self.conn.cursor()
        print("Opened {} with SQL version {}".format(self.file, sqlite3.version))

    def execute(self, sql):
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Error as e:
            print("Error: Database execute : {}".format(e))

    def insert(self, sql, values):
        try:
            self.cur.execute(sql, values)
            self.conn.commit()
        except Error as e:
            print("Error: Database insert : {}".format(e))

    def select(self, sql):
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Error as e:
            print("Error: Database select : {}".format(e))
        return self.cur.fetchall()

    def close(self):
        self.cur.close()
        self.conn.close()
        print("Closed database: {}".format(self.file))
        self.conn = None
        self.cur = None
        self.file = None
