# coding=utf-8
import os
import sqlite3


def query(db_path, sql):
    print('info: connect %s' % db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print(f'info: exec "{sql}" ')
    cursor.execute(sql)
    results = cursor.fetchall()
    return results
