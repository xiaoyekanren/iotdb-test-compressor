# coding=utf-8
import configparser
import os

from sql import query

cf = configparser.ConfigParser()
cf.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../config.ini'))

mark = 'iotdb_master_cb3eca69b1_20230712'
sqlite_path = '../example/results/results.db'


def main():
    sql = f"""
    select cpu_used_percent_list from system_monitor where 
    mark = \'{mark}\'
    and operate = 'query'
    and datatype = 'FLOAT'
    """

    query_results = query(sqlite_path, sql)
    print(query_results)
    for i in query_results:
        a = i[0]
        print(a)
        print(type(a))
        print('\n')
        break


if __name__ == '__main__':
    main()



